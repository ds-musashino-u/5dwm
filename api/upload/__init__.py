import time
import re
import json
import logging
import os
from io import BytesIO
from datetime import datetime, timezone
from uuid import uuid4
from base64 import b64decode
from urllib.request import urlopen, Request
from PIL import Image
from shared.auth import verify
from shared.imaging import resize_image

import azure.functions as func
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.cosmos.cosmos_client import CosmosClient


UPLOAD_MAX_FILESIZE = int(os.environ.get('UPLOAD_MAX_FILESIZE', '5000000'))


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        if req.headers['X-Authorization'].startswith('Bearer ') and not verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]):
            return func.HttpResponse(status_code=401, mimetype='', charset='')

        if req.headers['Content-Type'] == 'application/json':
            data = req.get_json()            
            match = re.match("data:([\\w/\\-\\.]+);(\\w+),(.+)", data.get('image'))
            
            if match:
                mime_type, encoding, data = match.groups()
            
                if encoding == 'base64':
                    container_name = '$web'
                    id = str(uuid4())
                    path = f'media/{id}'
                    decoded_data = b64decode(data)

                    if len(decoded_data) >= UPLOAD_MAX_FILESIZE:
                        return func.HttpResponse(status_code=413, mimetype='', charset='')
                    
                    blob_service_client = BlobServiceClient.from_connection_string(os.environ['AZURE_STORAGE_CONNECTION_STRING'])
                    container_client = blob_service_client.get_container_client(container_name)
                    
                    if mime_type in ['image/apng', 'image/gif', 'image/png', 'image/jpeg', 'image/webp']:
                        thumbnail_path = f'media/thumbnails/{id}'

                        thumbnail_image = resize_image(Image.open(BytesIO(decoded_data)), 8).convert('RGB')
                        thumbnail_bytes = BytesIO()
                        thumbnail_image.save(thumbnail_bytes, format='PNG')
                        
                        blob_client = container_client.get_blob_client(thumbnail_path)
                        blob_client.upload_blob(thumbnail_bytes.getvalue(), blob_type="BlockBlob", content_settings=ContentSettings(content_type=mime_type))
                    else:
                        thumbnail_path = None

                    blob_client = container_client.get_blob_client(path)
                    blob_client.upload_blob(decoded_data, blob_type="BlockBlob", content_settings=ContentSettings(content_type=mime_type))
                    
                    item = {'id': id, 'pk': id, 'url': f'https://5dwm.blob.core.windows.net/{container_name}/{path}', 'type': blob_client.get_blob_properties().content_settings.content_type, 'timestamp': datetime.fromtimestamp(time.time(), timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') }
                    
                    if thumbnail_path is not None:
                        item["thumbnail_url"] = f'https://5dwm.blob.core.windows.net/{container_name}/{thumbnail_path}'

                    client = CosmosClient.from_connection_string(os.environ['AZURE_COSMOS_DB_CONNECTION_STRING'])
                    database = client.get_database_client('5DWM')
                    container = database.get_container_client('Uploads')
                    container.upsert_item(item)

                    return func.HttpResponse(json.dumps(item), status_code=200, mimetype='application/json', charset='utf-8')

        return func.HttpResponse(status_code=400, mimetype='', charset='')

    except Exception as e:
        logging.error(f'{e}')

        return func.HttpResponse(json.dumps({
                'error': {
                    'message': str(e),
                    'type': type(e).__name__ }
            }),
            status_code=400,
            mimetype='application/json',
            charset='utf-8')
