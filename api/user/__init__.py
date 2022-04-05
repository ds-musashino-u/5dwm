import json
import logging
import os
from urllib.request import urlopen, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.models import User

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

        username = req.route_params.get('username')

        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            user = session.query(User).filter(User.username==username).one_or_none()
            
            if user is not None:
                user = {
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'updated_at': user.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                }

            return func.HttpResponse(json.dumps(user), status_code=200, mimetype='application/json', charset='utf-8')

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
