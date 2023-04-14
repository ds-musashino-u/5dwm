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
from sqlalchemy import create_engine, desc, or_
from sqlalchemy.orm import sessionmaker
from shared.auth import verify
from shared.imaging import compute_histogram, resize_image, top_k
from shared.models import Media, MediaFile, MediaData, ImageVector

import azure.functions as func


UPLOAD_MAX_FILESIZE = int(os.environ.get('UPLOAD_MAX_FILESIZE', '5000000'))

ssl._create_default_https_context = ssl._create_unverified_context
engine = create_engine(os.environ['POSTGRESQL_CONNECTION_URL'], connect_args={
                       'sslmode': 'disable'}, pool_recycle=60)


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
                            Image.open(BytesIO(b64decode(data))), 512).convert('RGB')), normalize='l1') * 100, 15)))

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
                                        Image.open(BytesIO(response.read())), 512).convert('RGB')), normalize='l1') * 100, 15)))

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
                                        resize_image(Image.open(bytes), 512).convert('RGB')), normalize='l1') * 100, 15)))

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
                query = session.query(Media)

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

                if histogram is not None:
                    query = query.join(ImageVector, Media.id == ImageVector.id).filter(Media.id.in_(session.query(ImageVector.id).filter(
                        or_(*list(map(lambda data: ImageVector.feature == f'f{data[0]}', histogram))))))

                    if limit is None:
                        limit = 15 * 100

                if keywords is not None:
                    for keyword in keywords:
                        query = query.filter(
                            Media.description.like(f'%{keyword}%'))

                if categories is not None and len(categories) > 0:
                    query = query.filter(or_(
                        *list(map(lambda category: Media.categories.contains([category]), categories))))

                if types is not None and len(types) > 0:
                    query = query.filter(
                        or_(*list(map(lambda type: Media.type.like(f'{type}%'), types))))

                if usernames is not None and len(usernames) > 0:
                    query = query.filter(
                        or_(*list(map(lambda username: Media.username == username, usernames))))

                if from_datetime is None:
                    query = query.filter(Media.created_at >=
                                         datetime(MINYEAR, 1, 1, 0, 0, 0, 0))
                else:
                    query = query.filter(Media.created_at >= datetime.fromisoformat(
                        from_datetime.replace('Z', '+00:00')))

                if to_datetime is not None:
                    query = query.filter(Media.created_at < datetime.fromisoformat(
                        to_datetime.replace('Z', '+00:00')))

                total_count = query.count()

                if limit is not None:
                    query = query.limit(limit)

                if offset is not None:
                    query = query.offset(offset)

                for item in query.all():
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
                            
                    medium = {
                        'id': item.id,
                        'url': item.url,
                        'type': item.type,
                        'categories': item.categories,
                        'address': item.address,
                        'description': item.description,
                        'username': item.username,
                        'location': {'type': 'Point', 'coordinates': [item.longitude, item.latitude]} if item.longitude is not None and item.latitude is not None else None,
                        'score': score,
                        'created_at': item.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                    }

                    if item.type.endswith('csv'):
                        media_file = session.query(MediaFile).filter(
                            MediaFile.media_id == item.id).one_or_none()

                        if media_file is not None:
                            limit = 100
                            query = session.query(MediaData).filter(
                                MediaData.file_id == media_file.id).limit(limit)
                            total_count = query.count()
                            data = []

                            for i in range(math.ceil(total_count / limit)):
                                q = query.offset(i * limit)

                                for media_data in q.all():
                                    data.append({
                                        'time': media_data.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                        'address': media_data.address,
                                        'location': {'type': 'Point', 'coordinates': [media_data.longitude, media_data.latitude]},
                                        'value': media_data.value
                                    })

                            medium['data'] = data

                    media.append(medium)

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
