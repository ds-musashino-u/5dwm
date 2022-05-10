import json
import logging
import os
import ssl
from urllib.request import urlopen, Request
from urllib.parse import quote
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from shared.auth import verify
from shared.models import Media

import azure.functions as func


ssl._create_default_https_context = ssl._create_unverified_context
engine = create_engine(os.environ['POSTGRESQL_CONNECTION_URL'], connect_args={
                       'sslmode': 'disable'}, pool_recycle=60)


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        if 'Authorization' in req.headers and req.headers['X-Authorization'].startswith('Bearer '):
            if not verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]):
                return func.HttpResponse(status_code=401, mimetype='', charset='')

        '''
        with psycopg2.connect(os.environ.get('POSTGRESQL_CONNECTION_URL'), sslmode='disable') as connection: #require
            with connection.cursor(cursor_factory=DictCursor) as cursol:
                cursol.execute('SELECT * FROM users')
                
                return func.HttpResponse(json.dumps([cursol.fetchall()]), status_code=200, mimetype='application/json', charset='utf-8')
        '''

        if req.headers.get('Content-Type') == 'application/json':
            data = req.get_json()
            keywords = data.get('keywords', [])
            categories = data.get('categories', [])
            types = data.get('types', [])
            usernames = data.get('usernames', [])
            image_url = data.get('image_url', '')
            sort = data['sort'] if 'sort' in data and data['sort'] is not None else 'created_at'
            order = data['order'] if 'order' in data and data['order'] is not None else 'desc'
            offset = data.get('offset')
            limit = data.get('limit')

            Session = sessionmaker(bind=engine)
            session = Session()

            try:
                media = []
                query = session.query(Media)

                if sort == 'created_at':
                    if order is None:
                        query = query.order_by(desc(Media.created_at))

                    else:
                        if order == 'asc':
                            query = query.order_by(Media.created_at)
                        elif order == 'desc':
                            query = query.order_by(desc(Media.created_at))
                        else:
                            return func.HttpResponse(status_code=400, mimetype='', charset='')

                else:
                    return func.HttpResponse(status_code=400, mimetype='', charset='')

                if limit is not None:
                    query = query.limit(limit)

                if offset is not None:
                    query = query.offset(offset)

                response = urlopen(Request(
                    f'https://www.5dwm.mydns.jp:8181/5dtest/QuerySearch?imgurl={quote(image_url)}&keyword={quote(",".join(keywords))}&ctg={quote(",".join(categories))}&kind={quote(",".join(types))}&db={quote(",".join(usernames))}', method='GET'))

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
                                'location': {'type': 'Point', 'coordinates': [item['lng'], item['lat']]},
                                # .strftime('%Y-%m-%dT%H:%M:%SZ')
                                'created_at': item['datetaken']
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
