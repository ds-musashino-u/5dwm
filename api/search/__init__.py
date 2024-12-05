import math
import re
import json
import logging
import os
import ssl
import numpy as np
from io import BytesIO
from datetime import datetime, timezone, MINYEAR
from base64 import b64decode
from urllib.request import urlopen, Request
from PIL import Image
from sqlalchemy import create_engine, desc, and_, or_
from sqlalchemy.orm import sessionmaker
from shared.auth import verify
from shared.imaging import compute_histogram, resize_image, top_k
from shared.models import Media, MediaFile, MediaData, MediaFileEx, MediaDataEx, ImageVector

import azure.functions as func


UPLOAD_MAX_FILESIZE = int(os.environ.get('UPLOAD_MAX_FILESIZE', '5000000'))
IMAGE_HISTOGRAM_TOP_K = 15
MAX_IMAGE_RESOLUTION = 512
MAX_IMAGE_SEARCH_RESULTS = 100

ssl._create_default_https_context = ssl._create_unverified_context
engine = create_engine(os.environ['POSTGRESQL_CONNECTION_URL'], connect_args={
                       'sslmode': 'require'}, pool_recycle=60)


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        if req.headers['X-Authorization'].startswith('Bearer '):
            if verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_API_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]) is None and verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]) is None:
                return func.HttpResponse(status_code=401, mimetype='', charset='')
        else:
            return func.HttpResponse(status_code=401, mimetype='', charset='')

        if req.headers.get('Content-Type') == 'application/json':
            data = req.get_json()
            keywords = data.get('keywords', None)
            categories = data.get('categories', None)
            types = data.get('types', None)
            usernames = data.get('usernames', None)
            image = data.get('image', None)
            location = data.get('location', None)
            collection = data.get('collection', None)
            from_datetime = data.get('from', None)
            to_datetime = data.get('to', None)
            sort = data['sort'] if 'sort' in data and data['sort'] is not None else 'created_at'
            order = data['order'] if 'order' in data and data['order'] is not None else 'desc'
            offset = data.get('offset')
            limit = data.get('limit')
            histogram = None
            start_time = datetime.now(timezone.utc).timestamp()

            Session = sessionmaker(bind=engine)
            session = Session()

            if image is not None:
                match = re.match("data:([\\w/\\-\\.]+);(\\w+),(.+)", image)

                if match:
                    mime_type, encoding, data = match.groups()

                    if mime_type in ['image/apng', 'image/gif', 'image/png', 'image/jpeg', 'image/webp'] and encoding == 'base64':
                        temp_histogram = list(filter(lambda x: x[1] > 0.0, top_k(compute_histogram(np.array(resize_image(
                            Image.open(BytesIO(b64decode(data))), MAX_IMAGE_RESOLUTION).convert('RGB')), normalize='l1') * 100, IMAGE_HISTOGRAM_TOP_K)))

                        if len(temp_histogram) > 0:
                            histogram = temp_histogram

                elif image.startswith('https://'):
                    response = urlopen(Request(image, method='HEAD'))

                    if response.getcode() == 200 and response.headers['Content-Type'] in ['image/apng', 'image/gif', 'image/png', 'image/jpeg', 'image/webp']:
                        if 'Content-Length' in response.headers:
                            if int(response.headers['Content-Length']) < UPLOAD_MAX_FILESIZE:
                                response = urlopen(Request(image))

                                if response.getcode() == 200:
                                    temp_histogram = list(filter(lambda x: x[1] > 0.0, top_k(compute_histogram(np.array(resize_image(
                                        Image.open(BytesIO(response.read())), MAX_IMAGE_RESOLUTION).convert('RGB')), normalize='l1') * 100, IMAGE_HISTOGRAM_TOP_K)))

                                    if len(temp_histogram) > 0:
                                        histogram = temp_histogram

                                else:
                                    return func.HttpResponse(status_code=response.getcode(), mimetype='', charset='')

                            else:
                                return func.HttpResponse(status_code=413, mimetype='', charset='')

                        else:
                            response = urlopen(Request(image))

                            if response.getcode() == 200:
                                bytes = BytesIO(response.read())

                                if bytes.getbuffer().nbytes < UPLOAD_MAX_FILESIZE:
                                    temp_histogram = list(filter(lambda x: x[1] > 0.0, top_k(compute_histogram(np.array(
                                        resize_image(Image.open(bytes), MAX_IMAGE_RESOLUTION).convert('RGB')), normalize='l1') * 100, IMAGE_HISTOGRAM_TOP_K)))

                                    if len(temp_histogram) > 0:
                                        histogram = temp_histogram

                                else:
                                    return func.HttpResponse(status_code=413, mimetype='', charset='')

                            else:
                                return func.HttpResponse(status_code=response.getcode(), mimetype='', charset='')

                    else:
                        return func.HttpResponse(status_code=response.getcode(), mimetype='', charset='')

                else:
                    return func.HttpResponse(status_code=400, mimetype='', charset='')

            try:
                media = []
                media_ids = []
                query = session.query(Media)
                filters = []
                subquery = None
                #subquery_ex = None
                
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
                        
                elif sort == 'id':
                    if order is None:
                        query = query.order_by(desc(Media.id))

                    else:
                        if order == 'asc':
                            query = query.order_by(Media.id)
                        elif order == 'desc':
                            query = query.order_by(desc(Media.id))
                        else:
                            return func.HttpResponse(status_code=400, mimetype='', charset='')

                else:
                    return func.HttpResponse(status_code=400, mimetype='', charset='')

                if histogram is not None:
                    query = query.join(ImageVector, Media.id == ImageVector.id)
                    filters.append(Media.id.in_(session.query(ImageVector.id.distinct()).filter(or_(*list(map(lambda data: ImageVector.feature == f'f{data[0]}', histogram))))))
                    limit = MAX_IMAGE_SEARCH_RESULTS * IMAGE_HISTOGRAM_TOP_K

                if keywords is not None:
                    for keyword in keywords:
                        filters.append(Media.description.ilike(f'%{keyword}%'))

                if categories is not None and len(categories) > 0:
                    filters.append(or_(*list(map(lambda category: Media.categories.contains([category]), categories))))
                    
                if types is not None and len(types) > 0:
                    filters.append(or_(*list(map(lambda type: Media.type.like(f'{type}%'), types))))
                    '''
                    if 'csv' in types and len(types) == 1:
                        subquery = session.query(MediaData.file_id.distinct())
                        subquery_ex = session.query(MediaDataEx.file_id.distinct())

                        if from_datetime is None:
                            subquery = subquery.filter(MediaData.time >= datetime(MINYEAR, 1, 1, 0, 0, 0, 0))
                            subquery_ex = subquery_ex.filter(MediaDataEx.time >= datetime(MINYEAR, 1, 1, 0, 0, 0, 0))
                        else:
                            subquery = subquery.filter(MediaData.time >= datetime.fromisoformat(from_datetime.replace('Z', '+00:00')))
                            subquery_ex = subquery_ex.filter(MediaDataEx.time >= datetime.fromisoformat(from_datetime.replace('Z', '+00:00')))
                        
                        if to_datetime is not None:
                            subquery = subquery.filter(MediaData.time < datetime.fromisoformat(to_datetime.replace('Z', '+00:00')))
                            subquery_ex = subquery_ex.filter(MediaDataEx.time < datetime.fromisoformat(to_datetime.replace('Z', '+00:00')))
                    '''
                '''
                else:
                    subquery = session.query(MediaData.file_id.distinct())
                    subquery_ex = session.query(MediaDataEx.file_id.distinct())

                    if from_datetime is None:
                        subquery = subquery.filter(MediaData.time >= datetime(MINYEAR, 1, 1, 0, 0, 0, 0))
                        subquery_ex = subquery_ex.filter(MediaDataEx.time >= datetime(MINYEAR, 1, 1, 0, 0, 0, 0))
                    else:
                        subquery = subquery.filter(MediaData.time >= datetime.fromisoformat(from_datetime.replace('Z', '+00:00')))
                        subquery_ex = subquery_ex.filter(MediaDataEx.time >= datetime.fromisoformat(from_datetime.replace('Z', '+00:00')))
                    
                    if to_datetime is not None:
                        subquery = subquery.filter(MediaData.time < datetime.fromisoformat(to_datetime.replace('Z', '+00:00')))
                        subquery_ex = subquery_ex.filter(MediaDataEx.time < datetime.fromisoformat(to_datetime.replace('Z', '+00:00')))
                '''
                if usernames is not None and len(usernames) > 0:
                    filters.append(or_(*list(map(lambda username: Media.username == username, usernames))))

                if location is not None and 'type' in location and location['type'] == 'Point' and 'coordinates' in location and isinstance(location['coordinates'], list):
                    filters.append(Media.longitude == location['coordinates'][0])
                    filters.append(Media.latitude == location['coordinates'][1])

                if collection is not None and len(collection) > 0:
                    filters.append(Media.collection == collection)

                if subquery is None:
                    if from_datetime is None:
                        filters.append(Media.created_at >= datetime(MINYEAR, 1, 1, 0, 0, 0, 0))
                    else:
                        filters.append(Media.created_at >= datetime.fromisoformat(from_datetime.replace('Z', '+00:00')))

                    if to_datetime is not None:
                        filters.append(Media.created_at < datetime.fromisoformat(to_datetime.replace('Z', '+00:00')))

                    query = query.filter(and_(*filters))
                        
                else:
                    '''
                    if keywords is not None:
                        for keyword in keywords:
                            subquery = subquery.filter(MediaFile.description.ilike(f'%{keyword}%'))
                            subquery_ex = subquery_ex.filter(MediaFileEx.description.ilike(f'%{keyword}%'))

                    if categories is not None and len(categories) > 0:
                        subquery = subquery.filter(or_(*list(map(lambda category: MediaFile.categories.contains([category]), categories))))
                        subquery_ex = subquery_ex.filter(or_(*list(map(lambda category: MediaFileEx.categories.contains([category]), categories))))

                    if usernames is not None and len(usernames) > 0:
                        subquery = subquery.filter(or_(*list(map(lambda username: MediaFile.username == username, usernames))))
                        subquery_ex = subquery_ex.filter(or_(*list(map(lambda username: MediaFileEx.username == username, usernames))))

                    operators = Media.id.in_(session.query(MediaFile.media_id).filter(MediaFile.id.in_(subquery)))
                    operators_ex = Media.id.in_(session.query(MediaFileEx.media_id).filter(MediaFileEx.id.in_(subquery_ex)))
                    
                    if to_datetime is None:
                        filters.append(Media.created_at >= (datetime(MINYEAR, 1, 1, 0, 0, 0, 0) if from_datetime is None else datetime.fromisoformat(from_datetime.replace('Z', '+00:00'))))
                    else:
                        filters.append(and_(Media.created_at >= (datetime(MINYEAR, 1, 1, 0, 0, 0, 0) if from_datetime is None else datetime.fromisoformat(from_datetime.replace('Z', '+00:00')))))
                        filters.append(Media.created_at < (datetime.fromisoformat(to_datetime.replace('Z', '+00:00'))))
                    
                    query = query.filter(or_(and_(*filters), operators))
                    '''
                    filters.append(Media.created_at >= datetime(MINYEAR, 1, 1, 0, 0, 0, 0))
                    query = query.filter(and_(*filters))
                
                total_count = query.count()

                if limit is not None:
                    query = query.limit(limit)

                if offset is not None:
                    query = query.offset(offset)

                for item in query.all():
                    if next((m for m in media if m['id'] == item.id), None) is None:
                        score = None

                        if histogram is not None and item.vector is not None:
                            vector1 = []
                            vector2 = []

                            for (index, value) in histogram:
                                for element in item.vector:
                                    if element.value > 0.0 and f'f{index}' == element.feature:
                                        vector1.append(value)
                                        vector2.append(element.value)

                            if len(vector1) > 0:
                                score = np.dot(np.array(vector1),
                                            np.array(vector2))
                                
                            total_count -= len(item.vector) - 1
                                
                        medium = {
                            'id': item.id,
                            'url': item.url,
                            'type': item.type,
                            'categories': item.categories,
                            'address': item.address,
                            'description': item.description,
                            'username': item.username,
                            'location': {'type': 'Point', 'coordinates': [item.longitude, item.latitude]} if item.longitude is not None and item.latitude is not None else None,
                            'collection': item.collection,
                            'score': score,
                            'created_at': item.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                        }

                        if item.type.endswith('csv'):
                            media_ids.append(item.id)
                            '''
                            media_file = session.query(MediaFile).filter(MediaFile.media_id == item.id).one_or_none()
                            
                            if media_file is None:
                                media_file = session.query(MediaFileEx).filter(MediaFileEx.media_id == item.id).one_or_none()

                                if media_file is not None:
                                    medium['data'] = {'types': media_file.types, 'items': []}

                                    limit = 100
                                    query = session.query(MediaDataEx).filter(MediaDataEx.file_id == media_file.id, MediaDataEx.time >= (datetime(MINYEAR, 1, 1, 0, 0, 0, 0) if from_datetime is None else datetime.fromisoformat(from_datetime.replace('Z', '+00:00'))))
                            
                                    if to_datetime is not None:
                                        query = query.filter(MediaDataEx.time < datetime.fromisoformat(to_datetime.replace('Z', '+00:00')))

                                    query = query.limit(limit)
                                    count = query.count()
                                    medium['data_types'] = media_file.types
                                    medium['data'] = []
                                    
                                    for i in range(math.ceil(count / limit)):
                                        for media_data in query.offset(i * limit).all():
                                            medium['data'].append({
                                                'id': media_data.id,
                                                'values': list(map(lambda x: None if math.isnan(x) else x, media_data.values)),
                                                'time': media_data.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                                'address': media_data.address,
                                                'location': {'type': 'Point', 'coordinates': [media_data.longitude, media_data.latitude]}
                                            })

                            else:
                                medium['data'] = {'types': [], 'items': []}

                                limit = 100
                                query = session.query(MediaData).filter(MediaData.file_id == media_file.id, MediaData.time >= (datetime(MINYEAR, 1, 1, 0, 0, 0, 0) if from_datetime is None else datetime.fromisoformat(from_datetime.replace('Z', '+00:00'))))
                            
                                if to_datetime is not None:
                                    query = query.filter(MediaData.time < datetime.fromisoformat(to_datetime.replace('Z', '+00:00')))

                                query = query.limit(limit)
                                count = query.count()
                                medium['data'] = []

                                for i in range(math.ceil(count / limit)):
                                    for media_data in query.offset(i * limit).all():
                                        medium['data'].append({
                                            'id': media_data.id,
                                            'time': media_data.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                            'address': media_data.address,
                                            'location': {'type': 'Point', 'coordinates': [media_data.longitude, media_data.latitude]},
                                            'value': media_data.value
                                        })
                            '''
                        
                        media.append(medium)

                    elif item.vector is not None:
                        total_count -= len(item.vector)

                    else:
                        total_count -= 1

                if histogram is not None:
                    total_count = min(total_count, MAX_IMAGE_SEARCH_RESULTS)

                if len(media_ids) > 0:
                    media_types = {}
                    limit = 100
                    subquery = session.query(MediaFile).filter(MediaFile.media_id.in_(media_ids))
                    count = subquery.count()
                    subquery = subquery.limit(limit)

                    for index in range(math.ceil(count / limit)):
                        for media_file in subquery.offset(index * limit).all():
                            media_types[media_file.media_id] = []

                    subquery = session.query(MediaFileEx).filter(MediaFileEx.media_id.in_(media_ids))
                    count = subquery.count()
                    subquery = subquery.limit(limit)

                    for index in range(math.ceil(count / limit)):
                        for media_file in subquery.offset(index * limit).all():
                            media_types[media_file.media_id] = media_file.types

                    for medium in media:
                        if medium['id'] in media_types:
                            medium['data'] = {'types': media_types[medium['id']], 'items': []}

                end_time = datetime.now(timezone.utc).timestamp()

                return func.HttpResponse(json.dumps({'count': total_count, 'timestamp': int(end_time), 'took': round(end_time - start_time, 3), 'items': media}), status_code=200, mimetype='application/json', charset='utf-8')

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
