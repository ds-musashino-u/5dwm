import time
import re
import json
import logging
import os
import pillow_heif
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
        if req.headers['X-Authorization'].startswith('Bearer '):
            if verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_API_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]) is None and verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]) is None:
                return func.HttpResponse(status_code=401, mimetype='', charset='')
        else:
            return func.HttpResponse(status_code=401, mimetype='', charset='')
        
        content_type = req.headers.get('Content-Type')

        if content_type == 'application/json':
            json_data = req.get_json()
            match = re.match("data:([\\w/\\-\\.]+);(\\w+),(.+)", json_data['data'])
            
            if match:
                mime_type, encoding, data = match.groups()
            
                if encoding == 'base64':
                    container_name = 'media'
                    id = str(uuid4())
                    path = id
                    decoded_data = b64decode(data)

                    if len(decoded_data) >= UPLOAD_MAX_FILESIZE:
                        return func.HttpResponse(status_code=413, mimetype='', charset='')
                    
                    blob_service_client = BlobServiceClient.from_connection_string(os.environ['AZURE_STORAGE_CONNECTION_STRING'])
                    container_client = blob_service_client.get_container_client(container_name)
                    
                    if mime_type in ['image/apng', 'image/gif', 'image/png', 'image/jpeg', 'image/webp']:
                        thumbnail_path = f'thumbnails/{id}'
                        thumbnail_type = 'image/jpeg'
                        stream = BytesIO(decoded_data)

                        if mime_type.startswith('image/heic') or mime_type.startswith('image/heif'):
                            heif_file = pillow_heif.read_heif(stream)
                            image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, 'raw', heif_file.mode, heif_file.stride)
                        else:
                            image = Image.open(stream)

                        thumbnail_image = resize_image(image, 512).convert('RGB')
                        thumbnail_bytes = BytesIO()
                        thumbnail_image.save(thumbnail_bytes, format='JPEG', quality=75)
                        
                        blob_client = container_client.get_blob_client(thumbnail_path)
                        blob_client.upload_blob(thumbnail_bytes.getvalue(), blob_type="BlockBlob", content_settings=ContentSettings(content_type=thumbnail_type))
                        
                        thumbnail = {'url': f'https://static.5dworldmap.com/{container_name}/{thumbnail_path}', 'type': thumbnail_type}
                    else:
                        thumbnail = None

                    blob_client = container_client.get_blob_client(path)

                    if blob_client.exists():
                        return func.HttpResponse(status_code=409, mimetype='', charset='')
                    
                    blob_client.upload_blob(decoded_data, blob_type="BlockBlob", content_settings=ContentSettings(content_type=mime_type))
                    
                    item = {'id': id, 'pk': id, 'url': f'https://static.5dworldmap.com/{container_name}/{path}', 'type': blob_client.get_blob_properties().content_settings.content_type, 'timestamp': datetime.fromtimestamp(time.time(), timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') }
                    
                    if thumbnail is not None:
                        item["thumbnail"] = thumbnail

                    client = CosmosClient.from_connection_string(os.environ['AZURE_COSMOS_DB_CONNECTION_STRING'])
                    database = client.get_database_client('5DWM')
                    container = database.get_container_client('Uploads')
                    container.upsert_item(item)

                    item["created_at"] = item["timestamp"]

                    del item["pk"]
                    del item["timestamp"]

                    return func.HttpResponse(json.dumps(item), status_code=201, mimetype='application/json', charset='utf-8')

        elif content_type.startswith('multipart/form-data;'):
            uploads = []
            
            for file in req.files.values():
                container_name = 'media'
                id = str(uuid4())
                path = id
                
                file.stream.seek(0, os.SEEK_END)
                cotent_length = file.stream.tell()
                
                if cotent_length >= UPLOAD_MAX_FILESIZE:
                    return func.HttpResponse(status_code=413, mimetype='', charset='')
                
                file.stream.seek(0)
                
                blob_service_client = BlobServiceClient.from_connection_string(os.environ['AZURE_STORAGE_CONNECTION_STRING'])
                container_client = blob_service_client.get_container_client(container_name)
                
                if file.content_type.startswith('image/'):
                    thumbnail_path = f'thumbnails/{id}'
                    thumbnail_type = 'image/jpeg'



                    thumbnail_image = resize_image(Image.open(file.stream), 512).convert('RGB')
                    thumbnail_bytes = BytesIO()
                    thumbnail_image.save(thumbnail_bytes, format='JPEG', quality=75)
                    file.stream.seek(0)
                    
                    blob_client = container_client.get_blob_client(thumbnail_path)
                    blob_client.upload_blob(thumbnail_bytes.getvalue(), blob_type="BlockBlob", content_settings=ContentSettings(content_type=thumbnail_type))
                    
                    thumbnail = {'url': f'https://static.5dworldmap.com/{container_name}/{thumbnail_path}', 'type': thumbnail_type}
                else:
                    thumbnail = None

                blob_client = container_client.get_blob_client(path)

                if blob_client.exists():
                    return func.HttpResponse(status_code=409, mimetype='', charset='')
                
                blob_client.upload_blob(file.stream, blob_type="BlockBlob", content_settings=ContentSettings(content_type=file.content_type))
                metadata = blob_client.get_blob_properties().metadata
                metadata.update({'filename': file.filename})
                blob_client.set_blob_metadata(metadata=metadata)
                    
                item = {'id': id, 'pk': id, 'url': f'https://static.5dworldmap.com/{container_name}/{path}', 'type': blob_client.get_blob_properties().content_settings.content_type, 'timestamp': datetime.fromtimestamp(time.time(), timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') }
                
                if thumbnail is not None:
                    item["thumbnail"] = thumbnail

                client = CosmosClient.from_connection_string(os.environ['AZURE_COSMOS_DB_CONNECTION_STRING'])
                database = client.get_database_client('5DWM')
                container = database.get_container_client('Uploads')
                container.upsert_item(item)

                item["created_at"] = item["timestamp"]

                del item["pk"]
                del item["timestamp"]

                uploads.append(item)
            
            if len(uploads) > 0:
                return func.HttpResponse(json.dumps(uploads[0] if len(uploads) == 1 else uploads), status_code=201, mimetype='application/json', charset='utf-8')

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
