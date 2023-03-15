import json
import logging
import os
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.auth import verify
from shared.models import Category

import azure.functions as func


engine = create_engine(os.environ['POSTGRESQL_CONNECTION_URL'], connect_args={
                       'sslmode': 'require'}, pool_recycle=60)


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        if req.method == 'GET':
            if req.headers.get('Content-Type') == 'application/json':
                data = req.get_json()
                offset = data.get('offset')
                limit = data.get('limit')

            else:
                offset = int(req.params['offset']
                             ) if 'offset' in req.params else None
                limit = int(req.params['limit']
                            ) if 'limit' in req.params else None

            Session = sessionmaker(bind=engine)
            session = Session()

            try:
                categories = []
                query = session.query(Category).order_by(Category.name)

                if limit is not None:
                    query = query.limit(limit)

                if offset is not None:
                    query = query.offset(offset)

                for category in query.all():
                    categories.append({
                        'id': category.id,
                        'name': category.name,
                        'updated_at': category.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                    })

                return func.HttpResponse(json.dumps(categories), status_code=200, mimetype='application/json', charset='utf-8')

            finally:
                session.close()

        elif req.method == 'POST':
            if req.headers['X-Authorization'].startswith('Bearer '):
                payload = verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_API_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]) is None and verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']])
                
                if payload is None or 'permissions' in payload and 'create:all' not in payload['permissions']:
                    return func.HttpResponse(status_code=401, mimetype='', charset='')

            else:
                return func.HttpResponse(status_code=401, mimetype='', charset='')
            
            if req.headers.get('Content-Type') == 'application/json':
                name = req.get_json()['name']

                if type(name) != str:
                    return func.HttpResponse(status_code=400, mimetype='', charset='')

                Session = sessionmaker(bind=engine)
                session = Session()

                try:
                    category = Category()
                    category.name = name
                    category.updated_at = datetime.now(timezone.utc)

                    session.add(category)
                    session.commit()

                    return func.HttpResponse(json.dumps({
                        'id': category.id,
                        'name': category.name,
                        'updated_at': category.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                    }), status_code=201, mimetype='application/json', charset='utf-8')

                except Exception as e:
                    session.rollback()

                    raise e

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
