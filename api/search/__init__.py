import json
import logging
import os
import ssl
from datetime import datetime, timezone
from sqlalchemy import create_engine, desc, or_
from sqlalchemy.orm import sessionmaker
from shared.auth import verify
from shared.models import Media

import azure.functions as func


ssl._create_default_https_context = ssl._create_unverified_context
engine = create_engine(os.environ['POSTGRESQL_CONNECTION_URL'], connect_args={
                       'sslmode': 'disable'}, pool_recycle=60)


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        if 'X-Authorization' in req.headers and req.headers['X-Authorization'].startswith('Bearer '):
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
            keywords = data.get('keywords', None)
            categories = data.get('categories', None)
            types = data.get('types', None)
            usernames = data.get('usernames', None)
            image_url = data.get('image_url', None)
            sort = data['sort'] if 'sort' in data and data['sort'] is not None else 'created_at'
            order = data['order'] if 'order' in data and data['order'] is not None else 'desc'
            offset = data.get('offset')
            limit = data.get('limit')
            start_time = datetime.now(timezone.utc).timestamp()

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

                if keywords is not None:
                    for keyword in keywords:
                        query = query.filter(
                            Media.description.like(f'%{keyword}%'))

                if categories is not None and len(categories) > 0:
                    query = query.filter(Media.categories.contains(categories))

                if types is not None and len(types) > 0:
                    query = query.filter(
                        or_(*list(map(lambda type: Media.type.like(f'{type}%'), types))))

                if usernames is not None and len(usernames) > 0:
                    query = query.filter(
                        or_(*list(map(lambda username: Media.username == username, usernames))))

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
                        'location': {'type': 'Point', 'coordinates': [item.longitude, item.latitude]} if item.longitude is not None and item.latitude is not None else None,
                        'created_at': item.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                    })

                return func.HttpResponse(json.dumps({'count': query.count(), 'took': round(datetime.now(timezone.utc).timestamp() - start_time, 3), 'items': media}), status_code=200, mimetype='application/json', charset='utf-8')

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
