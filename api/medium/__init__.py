import json
import logging
import os
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
        id = int(req.route_params.get('id'))
        Session = sessionmaker(bind=engine)
        session = Session()

        if req.method == 'DELETE':
            if 'X-Authorization' in req.headers and req.headers['X-Authorization'].startswith('Bearer '):
                if not verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]):
                    return func.HttpResponse(status_code=401, mimetype='', charset='')

            try:
                media = session.query(Media).filter(Media.id == id).one()

                session.delete(media)
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
                }), status_code=200, mimetype='application/json', charset='utf-8')

            except Exception as e:
                session.rollback()

                raise e

            finally:
                session.close()

        elif req.method == 'PUT':
            if 'X-Authorization' in req.headers and req.headers['X-Authorization'].startswith('Bearer '):
                if not verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]):
                    return func.HttpResponse(status_code=401, mimetype='', charset='')

            if req.headers.get('Content-Type') == 'application/json':
                data = req.get_json()
                url = data.get('url')

                try:
                    media = session.query(Media).filter(Media.id == id).one()
                    
                    if url is not None:
                        media.url = url

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
                    }), status_code=200, mimetype='application/json', charset='utf-8')

                except Exception as e:
                    session.rollback()

                    raise e

                finally:
                    session.close()

            else:
                return func.HttpResponse(status_code=400, mimetype='', charset='')

        else:
            try:
                media = session.query(Media).filter(
                    Media.id == id).one_or_none()

                if media is not None:
                    media = {
                        'id': media.id,
                        'url': media.url,
                        'type': media.type,
                        'categories': media.categories,
                        'address': media.address,
                        'description': media.description,
                        'username': media.username,
                        'location': {'type': 'Point', 'coordinates': [media.longitude, media.latitude]},
                        'created_at': media.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                    }

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
