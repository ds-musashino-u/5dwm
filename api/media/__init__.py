import imp
import json
import logging
import os
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from shared.auth import verify
from shared.models import Media

import azure.functions as func


engine = create_engine(os.environ['POSTGRESQL_CONNECTION_URL'], connect_args={
                       'sslmode': 'require'}, pool_recycle=60)


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
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
                limit = int(req.params['limit']
                            ) if 'limit' in req.params else None

            Session = sessionmaker(bind=engine)
            session = Session()

            try:
                media = []
                query = session.query(Media)

                if mime_type is not None:
                    query = query.filter(Media.type.like(
                        mime_type.replace('*', '%')))

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

        elif req.method == 'POST' and req.headers.get('Content-Type') == 'application/json':
            if 'X-Authorization' in req.headers and req.headers['X-Authorization'].startswith('Bearer '):
                if not verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]):
                    return func.HttpResponse(status_code=401, mimetype='', charset='')

            data = req.get_json()
            url = data['url']
            mime_type = data['type']
            categories = data['categories']
            address = data['address']
            description = data['description']
            username = data['username']
            longitude = data['location']['coordinates'][0]
            latitude = data['location']['coordinates'][1]

            if type(url) != str and type(mime_type) != str and type(categories) != list and type(address) != str and type(description) != str and type(username) != str and data['location']['type'] != 'Point':
                return func.HttpResponse(status_code=400, mimetype='', charset='')

            Session = sessionmaker(bind=engine)
            session = Session()

            try:
                media = Media()
                media.url = url
                media.type = mime_type
                media.categories = categories
                media.address = address
                media.description = description
                media.username = username
                media.latitude = latitude
                media.longitude = longitude
                media.created_at = datetime.now(timezone.utc)

                session.add(media)
                session.commit()

                return func.HttpResponse(json.dumps({
                    'id': media.id,
                    'url': media.url,
                    'type': media.type,
                    'categories': media.categories,
                    'address': media.address,
                    'description': media.description,
                    'username': media.username,
                    'location': {'type': 'Point', 'coordinates': [media.longitude, media.latitude]},
                    'created_at': media.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                }), status_code=201, mimetype='application/json', charset='utf-8')

            except Exception as e:
                session.rollback()

                raise e

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
