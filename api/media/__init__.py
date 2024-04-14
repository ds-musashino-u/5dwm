import math
import json
import logging
import os
import numpy as np
from io import BytesIO
from datetime import datetime, timezone, MINYEAR
from base64 import b64decode
from urllib.request import urlopen, Request
from PIL import Image
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from shared.auth import verify
from shared.imaging import compute_histogram, resize_image, top_k
from shared.models import Media, MediaFile, MediaData, MediaFileEx, MediaDataEx, ImageVector

import azure.functions as func


IMAGE_HISTOGRAM_TOP_K = 15
MAX_IMAGE_RESOLUTION = 512

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

                query = query.filter(Media.created_at >=
                                     datetime(MINYEAR, 1, 1, 0, 0, 0, 0))

                if limit is not None:
                    query = query.limit(limit)

                if offset is not None:
                    query = query.offset(offset)

                for item in query.all():
                    medium = {
                        'id': item.id,
                        'url': item.url,
                        'type': item.type,
                        'categories': item.categories,
                        'address': item.address,
                        'description': item.description,
                        'username': item.username,
                        'location': {'type': 'Point', 'coordinates': [item.longitude, item.latitude]},
                        'created_at': item.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                    }

                    if item.type.endswith('csv'):
                        media_file = session.query(MediaFile).filter(MediaFile.media_id == item.id).one_or_none()
                        
                        if media_file is None:
                            media_file = session.query(MediaFileEx).filter(MediaFileEx.media_id == item.id).one_or_none()

                            if media_file is not None:
                                limit = 100.0
                                query = session.query(MediaDataEx).filter(MediaDataEx.file_id == media_file.id).limit(limit)
                                count = query.count()
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

                                medium['data'] = {'types': media_file.types, 'items': data_items}

                        else:
                            limit = 100.0
                            query = session.query(MediaData).filter(MediaData.file_id == media_file.id).limit(limit)
                            count = query.count()
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

                            medium['data'] = {'types': [], 'items': data_items}

                    media.append(medium)

                return func.HttpResponse(json.dumps(media), status_code=200, mimetype='application/json', charset='utf-8')

            finally:
                session.close()

        elif req.method == 'POST' and req.headers.get('Content-Type') == 'application/json':
            if req.headers['X-Authorization'].startswith('Bearer '):
                if verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_API_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]) is None and verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]) is None:
                    return func.HttpResponse(status_code=401, mimetype='', charset='')
            else:
                return func.HttpResponse(status_code=401, mimetype='', charset='')

            data = req.get_json()
            url = data['url']
            mime_type = data['type']
            categories = data['categories']
            address = data['address'] if 'address' in data else ''
            description = data['description']
            username = data['username']
            longitude = data['location']['coordinates'][0]
            latitude = data['location']['coordinates'][1]
            created_at = datetime.fromisoformat(data['created_at'].replace(
                'Z', '+00:00')) if 'created_at' in data else datetime.now(timezone.utc)

            if type(url) is not str or type(mime_type) is not str or type(categories) is not list or type(address) is not str or type(description) is not str or type(username) is not str or data['location']['type'] != 'Point':
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
                media.created_at = created_at

                session.add(media)
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

                if media.type.startswith('image'):
                    try:
                        response = urlopen(Request(media.url))

                        if response.getcode() == 200:
                            image_data = BytesIO(response.read())
                        else:
                            image_data = None

                    except:
                        image_data = None

                    if image_data is not None:
                        histogram = list(filter(lambda x: x[1] > 0.0, top_k(compute_histogram(np.array(resize_image(Image.open(
                            image_data), MAX_IMAGE_RESOLUTION).convert('RGB')), normalize='l1') * 100, IMAGE_HISTOGRAM_TOP_K)))

                        for index, value in histogram:
                            image_vector = ImageVector()
                            image_vector.id = media.id
                            image_vector.feature = f'f{index}'
                            image_vector.value = value

                            session.add(image_vector)
                            session.commit()

                elif media.type.endswith('csv') and 'data' in data:
                    if 'types' in data['data'] and len(data['data']['types']) > 0:
                        media_file = MediaFileEx()
                        media_file.filename = media.url
                        media_file.types = data['data']['types']
                        media_file.categories = categories
                        media_file.description = description
                        media_file.username = username
                        media_file.created_at = created_at
                        media_file.updated_at = created_at
                        media_file.media_id = media.id

                        session.add(media_file)
                        session.commit()
                        data_items = []

                        for data_item in data['data']['items']:
                            media_data = MediaDataEx()
                            media_data.id = int(data_item['id'])
                            media_data.file_id = media_file.id
                            media_data.value = list(map(lambda x: float('nan') if x is None else x, data_item['values']))
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
                        media_file = MediaFile()
                        media_file.filename = media.url
                        media_file.categories = categories
                        media_file.description = description
                        media_file.username = username
                        media_file.created_at = created_at
                        media_file.updated_at = created_at
                        media_file.media_id = media.id

                        session.add(media_file)
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

                return func.HttpResponse(json.dumps(item), status_code=201, mimetype='application/json', charset='utf-8')

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
