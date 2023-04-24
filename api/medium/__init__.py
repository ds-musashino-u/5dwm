import math
import json
import logging
import os
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from shared.auth import verify
from shared.models import Media, MediaFile, MediaData

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
                if verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_API_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]) is None and verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]) is None:
                    return func.HttpResponse(status_code=401, mimetype='', charset='')
            else:
                return func.HttpResponse(status_code=401, mimetype='', charset='')

            try:
                media = session.query(Media).filter(Media.id == id).one()
                session.delete(media)
                item = {
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

                if media.type.endswith('csv'):
                    media_file = session.query(MediaFile).filter(MediaFile.media_id == id).one_or_none()

                    if media_file is not None:
                        limit = 100
                        session.delete(media_file)
                        query = session.query(MediaData).filter(MediaData.file_id == media_file.id).limit(limit)
                        total_count = query.count()
                        data = []

                        for i in range(math.ceil(total_count / limit)):
                            for media_data in query.offset(i * limit).all():
                                session.delete(media_data)
                                data.append({
                                    'id': media_data.id,
                                    'time': media_data.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                    'address': media_data.address,
                                    'location': {'type': 'Point', 'coordinates': [media_data.longitude, media_data.latitude]},
                                    'value': media_data.value
                                })

                        item['data'] = data

                session.commit()

                return func.HttpResponse(json.dumps(item), status_code=200, mimetype='application/json', charset='utf-8')

            except Exception as e:
                session.rollback()

                raise e

            finally:
                session.close()

        elif req.method == 'PUT':
            if req.headers['X-Authorization'].startswith('Bearer '):
                if verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_API_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]) is None and verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]) is None:
                    return func.HttpResponse(status_code=401, mimetype='', charset='')
            else:
                return func.HttpResponse(status_code=401, mimetype='', charset='')

            if req.headers.get('Content-Type') == 'application/json':
                data = req.get_json()
                url = data.get('url')
                mimetype = data.get('type')
                categories = data.get('categories')
                address = data.get('address')
                description = data.get('description')
                location = data.get('location')
                created_at = data.get('created_at')

                try:
                    media = session.query(Media).filter(Media.id == id).one()

                    if url is not None:
                        media.url = url

                    if mimetype is not None:
                        media.type = mimetype

                    if categories is not None:
                        media.categories = categories

                    if address is not None:
                        media.address = address

                    if description is not None:
                        media.description = description

                    if location is not None:
                        media.longitude = location['coordinates'][0]
                        media.latitude = location['coordinates'][1]

                    if created_at is not None:
                        media.created_at = datetime.fromisoformat(
                            created_at.replace('Z', '+00:00'))
                    
                    session.commit()
                    item = {
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

                    if media.type.endswith('csv') and 'data' in data:
                        media_file = session.query(MediaFile).filter(MediaFile.media_id == id).one_or_none()

                        if media_file is not None:
                            updated_at = data.get('updated_at')

                            media_file.filename = media.url
                            media_file.categories = categories
                            media_file.description = description
                            media_file.username = media.username

                            if updated_at is None:
                                media_file.updated_at = datetime.now(timezone.utc)
                            else:
                                media_file.updated_at = updated_at
                            
                            session.commit()

                            limit = 100
                            query = session.query(MediaData).filter(MediaData.file_id == media_file.id).limit(limit)
                            total_count = query.count()
                            
                            for i in range(math.ceil(total_count / limit)):
                                for media_data in query.offset(i * limit).all():
                                    session.delete(media_data)

                            item['data'] = []

                            for data_item in data['data']:
                                media_data = MediaData()
                                media_data.id = data_item['id']
                                media_data.file_id = media_file.id
                                media_data.value = data_item['value']
                                media_data.time = datetime.fromisoformat(data_item['time'].replace('Z', '+00:00'))
                                media_data.address = data_item['address'] if 'address' in data_item else ''
                                media_data.longitude = data_item['location']['coordinates'][0]
                                media_data.latitude = data_item['location']['coordinates'][1]
                                session.add(media_data)
                                item['data'].append({
                                    'id': media_data.id,
                                    'value': media_data.value,
                                    'time': media_data.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                    'address': media_data.address,
                                    'location': {'type': 'Point', 'coordinates': [media_data.longitude, media_data.latitude]},
                                })

                            session.commit()

                    return func.HttpResponse(json.dumps(item), status_code=200, mimetype='application/json', charset='utf-8')

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
                    item = {
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

                    if media.type.endswith('csv'):
                        media_file = session.query(MediaFile).filter(
                            MediaFile.media_id == id).one_or_none()

                        if media_file is not None:
                            limit = 100
                            query = session.query(MediaData).filter(MediaData.file_id == media_file.id).limit(limit)
                            total_count = query.count()
                            item['data'] = []

                            for i in range(math.ceil(total_count / limit)):
                                for media_data in query.offset(i * limit).all():
                                    item['data'].append({
                                        'id': media_data.id,
                                        'time': media_data.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                        'address': media_data.address,
                                        'location': {'type': 'Point', 'coordinates': [media_data.longitude, media_data.latitude]},
                                        'value': media_data.value
                                    })

                return func.HttpResponse(json.dumps(item), status_code=200, mimetype='application/json', charset='utf-8')

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
