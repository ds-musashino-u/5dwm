import time
import re
import json
import logging
import os
from uuid import uuid4

import azure.functions as func
from azure.storage.blob import BlobServiceClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    headers = {'Content-Type': 'application/json'}

    if 'Origin' in req.headers:
        headers['Access-Control-Allow-Origin'] = req.headers['Origin']

    try:
        pattern = "data:([\\w/\\-\\.]+);(\\w+),(.+)"
        
        if req.headers['Content-Type'] == 'application/json':
            data = req.get_json()            
            match = re.match(pattern, data.get('image'))
            path = data.get('path')
            
        else:
            match = re.match(pattern, req.get_body.decode('utf-8'))
            path = req.params.get('path')

        if match:
            mime_type, encoding, data = match.groups()
        
            if mime_type in ['image/png', 'image/jpeg'] and encoding == 'base64':
                container_name = 'images'

                if path is None:
                    path = str(uuid4())
        
                blob_service_client = BlobServiceClient.from_connection_string(os.environ.get('AZURE_STORAGE_CONNECTION_STRING'))
                container_client = blob_service_client.get_container_client(container_name)
            
                blob_client = container_client.get_blob_client(path)
                blob_client.upload_blob(data, blob_type="BlockBlob")
                #download_stream = blob_client.download_blob()
                #download_stream.readall()

                return func.HttpResponse(json.dumps({
                        'path': path,
                        'timestamp': int(time.time())
                    }),
                    status_code=200,
                    headers=headers,
                    charset='utf-8')

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
