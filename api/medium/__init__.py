import math
import json
import logging
import os
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from shared.auth import verify
from shared.models import Media, MediaFile, MediaData, MediaFileEx, MediaDataEx, ImageVector

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
                item = {
                    'id': media.id,
                    'url': media.url,
                    'type': media.type,
                    'categories': media.categories,
                    'address': media.address,
                    'description': media.description,
                    'username': media.username,
                    'location': {'type': 'Point', 'coordinates': [media.longitude, media.latitude]},
                    'collection': media.collection,
                    'created_at': media.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                }

                if media.type.startswith('image'):
                    for image_vector in session.query(ImageVector).filter(ImageVector.id == id).all():
                        session.delete(image_vector)

                    session.commit()

                elif media.type.endswith('csv'):
                    media_file = session.query(MediaFile).filter(MediaFile.media_id == id).one_or_none()

                    if media_file is None:
                        media_file = session.query(MediaFileEx).filter(MediaFileEx.media_id == id).one_or_none()

                        if media_file is not None:
                            limit = 100
                            session.delete(media_file)
                            query = session.query(MediaDataEx).filter(MediaDataEx.file_id == media_file.id)
                            count = float(query.count())
                            query = query.limit(limit)
                            data_items = []

                            for i in range(math.ceil(count / limit)):
                                for media_data in query.offset(i * limit).all():
                                    session.delete(media_data)
                                    data_items.append({
                                        'id': media_data.id,
                                        'values': list(map(lambda x: None if math.isnan(x) else x, media_data.values)),
                                        'time': media_data.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                        'address': media_data.address,
                                        'location': {'type': 'Point', 'coordinates': [media_data.longitude, media_data.latitude]}
                                    })

                            item['data'] = {'types': media_file.types, 'items': data_items}

                    else:
                        limit = 100
                        session.delete(media_file)
                        query = session.query(MediaData).filter(MediaData.file_id == media_file.id)
                        count = float(query.count())
                        query = query.limit(limit)
                        data_items = []

                        for i in range(math.ceil(count / limit)):
                            for media_data in query.offset(i * limit).all():
                                session.delete(media_data)
                                data_items.append({
                                    'id': media_data.id,
                                    'values': [media_data.value],
                                    'time': media_data.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                    'address': media_data.address,
                                    'location': {'type': 'Point', 'coordinates': [media_data.longitude, media_data.latitude]}
                                })

                        item['data'] = {'types': [], 'items': data_items}

                session.delete(media)
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
                collection = data.get('collection')
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

                    if collection is not None:
                        media.collection = collection

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
                        'collection': None if media.collection is None else {'name': media.collection, 'items': []},
                        'created_at': media.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                    }

                    if media.type.endswith('csv') and 'data' in data:
                        media_file = session.query(MediaFile).filter(MediaFile.media_id == id).one_or_none()

                        if media_file is None:
                            media_file = session.query(MediaFileEx).filter(MediaFileEx.media_id == id).one_or_none()

                            if media_file is not None:
                                updated_at = data.get('updated_at')
                                
                                media_file.filename = media.url
                                media_file.categories = categories
                                media_file.description = description
                                media_file.username = media.username

                                if 'types' in data['data'] and len(data['data']['types']) > 0:
                                    media_file.types = data['data']['types']

                                if updated_at is None:
                                    media_file.updated_at = datetime.now(timezone.utc)
                                else:
                                    media_file.updated_at = updated_at

                                session.commit()

                                limit = 100
                                query = session.query(MediaDataEx).filter(MediaDataEx.file_id == media_file.id)
                                count = float(query.count())
                                query = query.limit(limit)

                                for i in range(math.ceil(count / limit)):
                                    for media_data in query.offset(i * limit).all():
                                        session.delete(media_data)

                                session.commit()

                                data_items = []

                                for data_item in data['data']['items']:
                                    media_data = MediaDataEx()
                                    media_data.id = int(data_item['id'])
                                    media_data.file_id = media_file.id
                                    media_data.values = list(map(lambda x: float('nan') if x is None else x, data_item['values']))
                                    media_data.time = datetime.fromisoformat(data_item['time'].replace('Z', '+00:00'))
                                    media_data.address = data_item['address'] if 'address' in data_item else ''
                                    media_data.longitude = data_item['location']['coordinates'][0]
                                    media_data.latitude = data_item['location']['coordinates'][1]
                                    session.add(media_data)
                                    data_items.append({
                                        'id': media_data.id,
                                        'values': list(map(lambda x: None if math.isnan(x) else x, media_data.values)),
                                        'time': media_data.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                        'address': media_data.address,
                                        'location': {'type': 'Point', 'coordinates': [media_data.longitude, media_data.latitude]}
                                    })

                                item['data'] = {'types': media_file.types, 'items': data_items}

                                session.commit()

                        else:
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
                            query = session.query(MediaData).filter(MediaData.file_id == media_file.id)
                            count = float(query.count())
                            query = query.limit(limit)
                            
                            for i in range(math.ceil(count / limit)):
                                for media_data in query.offset(i * limit).all():
                                    session.delete(media_data)

                            session.commit()

                            data_items = []

                            for data_item in data['data']['items']:
                                media_data = MediaData()
                                media_data.id = int(data_item['id'])
                                media_data.file_id = media_file.id
                                media_data.value = data_item['values'][0]
                                media_data.time = datetime.fromisoformat(data_item['time'].replace('Z', '+00:00'))
                                media_data.address = data_item['address'] if 'address' in data_item else ''
                                media_data.longitude = data_item['location']['coordinates'][0]
                                media_data.latitude = data_item['location']['coordinates'][1]
                                session.add(media_data)
                                data_items.append({
                                    'id': media_data.id,
                                    'values': [media_data.value],
                                    'time': media_data.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                    'address': media_data.address,
                                    'location': {'type': 'Point', 'coordinates': [media_data.longitude, media_data.latitude]}
                                })

                            item['data'] = {'types': [], 'items': data_items}

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
                media = session.query(Media).filter(Media.id == id).one_or_none()

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
                        'collection': None if media.collection is None else {'name': media.collection, 'items': []},
                        'created_at': media.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                    }

                    if media.type.endswith('csv'):
                        media_file = session.query(MediaFile).filter(
                            MediaFile.media_id == id).one_or_none()

                        if media_file is None:
                            media_file = session.query(MediaFileEx).filter(MediaFileEx.media_id == id).one_or_none()

                            if media_file is not None:
                                limit = 100
                                query = session.query(MediaDataEx).filter(MediaDataEx.file_id == media_file.id)
                                count = float(query.count())
                                query = query.limit(limit)
                                data_items = []
                                
                                for i in range(math.ceil(count / limit)):
                                    for media_data in query.offset(i * limit).all():
                                        data_items.append({
                                            'id': media_data.id,
                                            'values': list(map(lambda x: None if math.isnan(x) else x, media_data.values)),
                                            'time': media_data.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                            'address': media_data.address,
                                            'location': {'type': 'Point', 'coordinates': [media_data.longitude, media_data.latitude]}
                                        })

                                item['data'] = {'types': media_file.types, 'items': data_items}

                        else:
                            limit = 100
                            query = session.query(MediaData).filter(MediaData.file_id == media_file.id)
                            count = float(query.count())
                            query = query.limit(limit)
                            data_items = []

                            for i in range(math.ceil(count / limit)):
                                for media_data in query.offset(i * limit).all():
                                    data_items.append({
                                        'id': media_data.id,
                                        'values': [media_data.value],
                                        'time': media_data.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                        'address': media_data.address,
                                        'location': {'type': 'Point', 'coordinates': [media_data.longitude, media_data.latitude]}
                                    })

                            item['data'] = {'types': [], 'items': data_items}

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
