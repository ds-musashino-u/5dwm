import json
import logging
import ssl
from urllib.request import urlopen, Request

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    ssl._create_default_https_context = ssl._create_unverified_context

    try:
        if req.headers['Content-Type'] == 'application/json':
            data = req.get_json()            
            response = urlopen(Request(
                data['url'],
                method=req.method))

            if response.getcode() == 200:
                return func.HttpResponse(response.read(), status_code=200, mimetype=response.headers['Content-Type'], charset='utf-8')

        return func.HttpResponse(status_code=400, mimetype='', charset='')

    except Exception as e:
        logging.error(f'{e}')

        return func.HttpResponse(json.dumps({
            'error': {
                'message': str(e),
                'type': type(e).__name__}
        }),
            status_code=400,
            mimetype='application/json',
            charset='utf-8')
