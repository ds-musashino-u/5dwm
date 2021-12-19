import time
import json
import uuid
import logging
import os

import azure.functions as func
from azure.storage.blob import BlobServiceClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    headers = {'Content-Type': 'application/json'}

    if 'Origin' in req.headers:
        headers['Access-Control-Allow-Origin'] = req.headers['Origin']

    try:
        req_body = req.get_json()
        image = req_body.get("image")
        
        blob_service_client = BlobServiceClient.from_connection_string(os.environ.get("AZURE_STORAGE_CONNECTION_STRING"))
        container_client = blob_service_client.get_container_client("images")
    
        blob = str(uuid.uuid4())
        blob_client = container_client.get_blob_client(blob)
        #blob_client.upload_blob(data, blob_type="BlockBlob")
        #download_stream = blob_client.download_blob()
        #download_stream.readall()

        return func.HttpResponse(json.dumps({
                'blob': blob,
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
