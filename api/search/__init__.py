import json
import logging
import os
from urllib.request import urlopen, Request
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared import Base, User

import azure.functions as func


#engine = create_engine(os.environ.get('POSTGRESQL_CONNECTION_URL'), connect_args={'sslmode':'verify-full'}, pool_recycle=60)
#Base.metadata.bind = engine

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

        with psycopg2.connect(os.environ.get('POSTGRESQL_CONNECTION_URL'), sslmode='verify-full') as connection:
            with connection.cursor() as cursol:
                return func.HttpResponse(json.dumps([]), status_code=200, mimetype='application/json', charset='utf-8')

        
        return func.HttpResponse(json.dumps({
                    'timestamp': int(0)
                }),
                status_code=200,
                mimetype='application/json',
                charset='utf-8')
        
        
        #Session = sessionmaker(bind=engine)
        #session = Session()

        #try:
            #session.query(User).all()


        #finally:
            #session.close()


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
