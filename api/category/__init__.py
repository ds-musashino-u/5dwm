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
        id = int(req.route_params.get('id'))
        Session = sessionmaker(bind=engine)
        session = Session()

        if req.method == 'DELETE':
            if req.headers['X-Authorization'].startswith('Bearer '):
                payload = verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_API_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']])
                
                if payload is None or 'permissions' not in payload or 'delete:all' not in payload['permissions']:
                    return func.HttpResponse(status_code=401, mimetype='', charset='')

            else:
                return func.HttpResponse(status_code=401, mimetype='', charset='')
            
            try:
                category = session.query(Category).filter(
                    Category.id == id).one()

                session.delete(category)
                session.commit()

                return func.HttpResponse(json.dumps({
                    'id': category.id,
                    'name': category.name,
                    'updated_at': category.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                }), status_code=200, mimetype='application/json', charset='utf-8')

            except Exception as e:
                session.rollback()

                raise e

            finally:
                session.close()

        elif req.method == 'PUT':
            if req.headers['X-Authorization'].startswith('Bearer '):
                payload = verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_API_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']])
                
                if payload is None or 'permissions' not in payload or 'update:all' not in payload['permissions']:
                    return func.HttpResponse(status_code=401, mimetype='', charset='')

            else:
                return func.HttpResponse(status_code=401, mimetype='', charset='')
            
            if req.headers.get('Content-Type') == 'application/json':
                name = req.get_json()['name']

                try:
                    category = session.query(Category).filter(
                        Category.id == id).one()
                    category.name = name
                    category.updated_at = datetime.now(timezone.utc)

                    session.commit()

                    return func.HttpResponse(json.dumps({
                        'id': category.id,
                        'name': category.name,
                        'updated_at': category.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
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
                category = session.query(Category).filter(
                    Category.id == id).one_or_none()

                if category is not None:
                    category = {
                        'id': category.id,
                        'name': category.name,
                        'updated_at': category.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                    }

                return func.HttpResponse(json.dumps(category), status_code=200, mimetype='application/json', charset='utf-8')

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
