import json
import logging
import os
from urllib.request import urlopen, Request
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from shared.models import Media

import azure.functions as func


engine = create_engine(os.environ.get('POSTGRESQL_CONNECTION_URL'), connect_args={
                       'sslmode': 'require'}, pool_recycle=60)


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

        if req.method == 'GET':
            if req.headers.get('Content-Type') == 'application/json':
                data = req.get_json()
                mime_type = data.get('type')
                sort = data['sort'] if 'sort' in data and data['sort'] is not None else 'created_at'
                order = data['order'] if 'order' in data and data['order'] is not None else 'desc'
                offset = data.get('offset')
                limit = data.get('limit')

            else:
                mime_type = req.params['type'] if 'type' in req.params else None
                sort = req.params['sort'] if 'sort' in req.params else 'created_at'
                order = req.params['order'] if 'order' in req.params else 'desc'
                offset = int(req.params['offset']
                            ) if 'offset' in req.params else None
                limit = int(req.params['limit']) if 'limit' in req.params else None

            Session = sessionmaker(bind=engine)
            session = Session()

            try:
                media = []
                query = session.query(Media)

                if mime_type is not None:
                    query = query.filter(Media.type.like(mime_type.replace('*', '%')))

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

                for item in query.all():
                    media.append({
                        'id': item.id,
                        'url': item.url,
                        'type': item.type,
                        'categories': item.categories,
                        'address': item.address,
                        'description': item.description,
                        'username': item.username,
                        'location': {'type': 'Point', 'coordinates': [item.longitude, item.latitude]},
                        'created_at': item.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                    })

                return func.HttpResponse(json.dumps(media), status_code=200, mimetype='application/json', charset='utf-8')

            finally:
                session.close()

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
