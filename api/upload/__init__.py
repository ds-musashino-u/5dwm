import logging

import azure.functions as func
from azure.storage.blob import BlobServiceClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    #blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
    #container_client = blob_service_client.get_container_client("uploads")
    #blob_client = container_client.get_blob_client("myblockblob")
    #blob_client.upload_blob(data, blob_type="BlockBlob")
    #download_stream = blob_client.download_blob()
    #download_stream.readall()

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
