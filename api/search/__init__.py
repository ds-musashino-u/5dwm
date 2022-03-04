import json
import logging
import os
from urllib.request import urlopen, Request
import psycopg2
from psycopg2.extras import DictCursor
from sqlalchemy.orm import sessionmaker
from shared.models import engine, Base, User

import azure.functions as func


Base.metadata.bind = engine

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
        
        
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            users = []

            for user in session.query(User).all():
                users.append({'user_cns': user.user_cns})

            return func.HttpResponse(json.dumps(users), status_code=200, mimetype='application/json', charset='utf-8')
            
        finally:
            session.close()


        #with engine.connect() as connection:
        
        
        #return func.HttpResponse(json.dumps([]), status_code=200, mimetype='application/json', charset='utf-8')

        #return func.HttpResponse(status_code=400, mimetype='', charset='')

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
