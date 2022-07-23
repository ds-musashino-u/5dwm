import json
import logging
import os
import ssl
from base64 import b64encode
from urllib.request import urlopen, Request

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    ssl._create_default_https_context = ssl._create_unverified_context

    try:
        if req.headers['Content-Type'] == 'application/json':
            data = req.get_json()
            url = data['url']
            
            if url.startswith('https://www.5dwm.mydns.jp/'):
                authorization = b64encode(f"{os.environ['BASIC_AUTHENTICATION_USERNAME']}:{os.environ['BASIC_AUTHENTICATION_PASSWORD']}".encode('utf-8')).decode('utf-8')
                request = Request(
                url,
                method=req.method,
                headers={'Authorization': f"BASIC {authorization}"})
            
            else:
                request = Request(url, method=req.method)

            response = urlopen(request)

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