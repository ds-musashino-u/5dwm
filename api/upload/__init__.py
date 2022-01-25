import time
import re
import json
import logging
import os
from datetime import datetime, timezone
from uuid import uuid4
from base64 import b64decode
from urllib.request import urlopen, Request

import azure.functions as func
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.cosmos.cosmos_client import CosmosClient


def main(req: func.HttpRequest) -> func.HttpResponse:
    headers = {'Content-Type': 'application/json'}

    if 'Origin' in req.headers:
        headers['Access-Control-Allow-Origin'] = req.headers['Origin']

    try:
        if 'Authorization' in req.headers:
            '''
            jwt = req.headers['Authorization'].split(' ')[1].split('.') if req.headers['Authorization'].startswith('Bearer ') else req.headers['Authorization'].split('.')

            if json.loads(b64decode(jwt[0] + '=' * (-len(jwt[0]) % 4)))['typ'] == 'JWT' and json.loads(b64decode(jwt[1] + '=' * (-len(jwt[1]) % 4)))['iss'] == 'https://':
                try:
                    response = urlopen(Request(
                        f'https://',
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps({'idToken': req.headers['Authorization']}).encode('utf-8')))

                    if response.getcode() != 200:
                        raise Exception

                except Exception:
                    return func.HttpResponse(status_code=403, headers=headers)
            '''
            pass
        
        if req.headers['Content-Type'] == 'application/json':
            data = req.get_json()            
            match = re.match("data:([\\w/\\-\\.]+);(\\w+),(.+)", data.get('image'))
            
            if match:
                mime_type, encoding, data = match.groups()
            
                if mime_type in ['image/apng', 'image/gif', 'image/png', 'image/jpeg', 'image/webp'] and encoding == 'base64':
                    container_name = '$web'
                    id = str(uuid4())
                    path = f'images/{id}'
                    
                    blob_service_client = BlobServiceClient.from_connection_string(os.environ.get('AZURE_STORAGE_CONNECTION_STRING'))
                    container_client = blob_service_client.get_container_client(container_name)
                
                    blob_client = container_client.get_blob_client(path)
                    blob_client.upload_blob(b64decode(data), blob_type="BlockBlob", content_settings=ContentSettings(content_type=mime_type))
                    
                    item = {'id': id, 'pk': id, 'url': f'https://5dwm.blob.core.windows.net/{container_name}/{path}', 'type': mime_type, 'timestamp': datetime.fromtimestamp(time.time(), timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') }
                    
                    client = CosmosClient.from_connection_string(os.environ.get('AZURE_COSMOS_DB_CONNECTION_STRING'))
                    database = client.get_database_client('5DWM')
                    container = database.get_container_client('Uploads')
                    container.upsert_item(item)

                    return func.HttpResponse(json.dumps(item), status_code=200, headers=headers, charset='utf-8')

        return func.HttpResponse(status_code=400, headers=headers)

    except Exception as e:
        logging.error(f'{e}')

        return func.HttpResponse(json.dumps({
                'error': {
                    'message': str(e),
                    'type': type(e).__name__ }
            }),
            status_code=400,
            headers=headers,
            charset='utf-8')
