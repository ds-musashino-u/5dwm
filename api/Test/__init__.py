import logging
import time
import json
import os

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    headers = {'Content-Type': 'application/json'}

    if 'Origin' in req.headers:
        headers['Access-Control-Allow-Origin'] = req.headers['Origin']
    
    name = req.params.get('name')

    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        try:
            return func.HttpResponse(json.dumps({
                    'text': name,
                    'key': os.environ["ACCESS_KEY2"],
                    'timestamp': int(time.time())
                }),
                status_code=200,
                headers=headers,
                charset='utf-8')

        except Exception as e:
            return func.HttpResponse(json.dumps({
                    'error': {
                        'message': e.args,
                        'type': type(e).__name__ }
                }),
                status_code=400,
                headers=headers,
                charset='utf-8')

    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
        )
