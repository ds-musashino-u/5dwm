import json
import logging
import os
from base64 import b64decode
from urllib.request import urlopen, Request

import azure.functions as func
from azure.cosmos.cosmos_client import CosmosClient


def main(req: func.HttpRequest) -> func.HttpResponse:
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
                    return func.HttpResponse(status_code=403, mimetype='', charset='')
            '''
            pass
        
        if req.headers.get('Content-Type') == 'application/json':
            data = req.get_json()
            offset = data.get('offset')
            limit = data.get('limit')
            
        else:
            offset = int(req.params['offset']) if 'offset' in req.params else None
            limit = int(req.params['limit']) if 'limit' in req.params else None

        client = CosmosClient.from_connection_string(os.environ['AZURE_COSMOS_DB_CONNECTION_STRING'])
        database = client.get_database_client('5DWM')
        container = database.get_container_client('Uploads')
        items = list(container.query_items(
            query='SELECT u.id, u.url, u.type, u.timestamp FROM Uploads u ORDER BY u.timestamp DESC OFFSET @offset LIMIT @limit',
            parameters=[
                { "name":"@offset", "value": 0 if offset is None else offset },
                { "name":"@limit", "value": 100 if limit is None else limit }
            ],
            enable_cross_partition_query=True))

        return func.HttpResponse(json.dumps(items), status_code=200, mimetype='application/json', charset='utf-8')

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
