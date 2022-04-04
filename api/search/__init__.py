import json
import logging
import os
import ssl
from urllib.request import urlopen, Request
from urllib.parse import quote
from dateutil.parser import parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.models import Media

import azure.functions as func


ssl._create_default_https_context = ssl._create_unverified_context
engine = create_engine(os.environ.get('POSTGRESQL_CONNECTION_URL'), connect_args={
                       'sslmode': 'disable'}, pool_recycle=60)


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

        '''
        with psycopg2.connect(os.environ.get('POSTGRESQL_CONNECTION_URL'), sslmode='disable') as connection: #require
            with connection.cursor(cursor_factory=DictCursor) as cursol:
                cursol.execute('SELECT * FROM users')
                
                return func.HttpResponse(json.dumps([cursol.fetchall()]), status_code=200, mimetype='application/json', charset='utf-8')
        '''

        if req.headers.get('Content-Type') == 'application/json':
            data = req.get_json()
            keywords = data.get('keywords', [])
            sort = data['sort'] if 'sort' in data and data['sort'] is not None else 'created_at'
            order = data['order'] if 'order' in data and data['order'] is not None else 'desc'
            offset = data.get('offset')
            limit = data.get('limit')

            image_url = ""
            categories = "";
            kinds = ""
            databases = ""

            Session = sessionmaker(bind=engine)
            session = Session()

            try:
                media = []            
                response = urlopen(Request(f'https://www.5dwm.mydns.jp:8181/5dtest/QuerySearch?imgurl={quote(image_url)}&keyword={quote(",".join(keywords))}&ctg={quote(categories)}&kind={quote(kinds)}&db={quote(databases)}', method='GET'))

                if response.getcode() == 200:
                    for item in json.loads(response.read()):
                        if 'id' in item:
                            media.append({
                                'id': item['id'],
                                'url': item['file_name'],
                                'type': item['kind'],
                                'categories': [item['category']],
                                'address': item['place'],
                                'description': item['description'],
                                'username': item['user_cns'],
                                'latitude': item['lat'],
                                'longitude': item['lng'],
                                'created_at': parse(item['datetaken']).strftime('%Y-%m-%dT%H:%M:%SZ')
                            })
                
                    return func.HttpResponse(json.dumps(media), status_code=200, mimetype='application/json', charset='utf-8')

            finally:
                session.close()

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
