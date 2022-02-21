import random
import re
import json
import logging
import os
import hmac
from datetime import datetime, timezone
from base64 import b64encode, b64decode
from hashlib import sha1, md5
from urllib.parse import quote
from urllib.request import urlopen, Request

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
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
