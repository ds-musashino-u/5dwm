import json
import logging
import os
from urllib.request import urlopen, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.models import Category

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

        id = int(req.route_params.get('id'))
        Session = sessionmaker(bind=engine)
        session = Session()

        if req.method == 'DELETE':
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
            if req.headers.get('Content-Type') == 'application/json':
                name = req.get_json()['name']

                try:
                    category = session.query(Category).filter(
                        Category.id == id).one_or_none()

                    if category is not None:
                        category.name = name

                        category = {
                            'id': category.id,
                            'name': category.name,
                            'updated_at': category.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                        }

                    return func.HttpResponse(json.dumps(category), status_code=200, mimetype='application/json', charset='utf-8')

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
