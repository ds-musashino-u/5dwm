import logging
import time
import json

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    headers = {'Content-Type': 'application/json'}

    if 'HTTP_ORIGIN' in req.headers:
        headers['Access-Control-Allow-Origin'] = req.headers['HTTP_ORIGIN']
    
    name = req.params.get('name')

    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(json.dumps({
                'text': name,
                'timestamp': int(time.time())
            }),
            status_code=200,
            headers=headers,
            charset='utf-8')
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
        )
