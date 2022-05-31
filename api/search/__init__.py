import re
import json
import logging
import os
import ssl
import numpy as np
from io import BytesIO
from datetime import datetime, timezone
from base64 import b64decode
from urllib.request import urlopen, Request
from PIL import Image
from sqlalchemy import create_engine, desc, or_
from sqlalchemy.orm import sessionmaker
from shared.auth import verify
from shared.imaging import compute_histogram, resize_image, top_k
from shared.models import Media, ImageVector

import azure.functions as func


UPLOAD_MAX_FILESIZE = os.environ.get('UPLOAD_MAX_FILESIZE', 5000000)

ssl._create_default_https_context = ssl._create_unverified_context
engine = create_engine(os.environ['POSTGRESQL_CONNECTION_URL'], connect_args={
                       'sslmode': 'disable'}, pool_recycle=60)


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        if 'X-Authorization' in req.headers and req.headers['X-Authorization'].startswith('Bearer '):
            if not verify(req.headers['X-Authorization'].split(' ')[1], os.environ['AUTH0_JWKS_URL'], os.environ['AUTH0_AUDIENCE'], os.environ['AUTH0_ISSUER'], [os.environ['AUTH0_ALGORITHM']]):
                return func.HttpResponse(status_code=401, mimetype='', charset='')

        if req.headers.get('Content-Type') == 'application/json':
            data = req.get_json()
            keywords = data.get('keywords', None)
            categories = data.get('categories', None)
            types = data.get('types', None)
            usernames = data.get('usernames', None)
            image = data.get('image', None)
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
                            Image.open(BytesIO(b64decode(data))), 256).convert('RGB')), normalize='l1'), 15)))

                        if len(temp_histogram) > 0:
                            histogram = temp_histogram

                elif image.startswith('https://'):
                    response = urlopen(Request(image, method='HEAD'))

                    if response.getcode() == 200 and response.headers['Content-Type'] in ['image/apng', 'image/gif', 'image/png', 'image/jpeg', 'image/webp']:
                        if int(response.headers['Content-Length']) < UPLOAD_MAX_FILESIZE:
                            response = urlopen(Request(image))

                            if response.getcode() == 200:
                                temp_histogram = list(filter(lambda x: x[1] > 0.0, top_k(compute_histogram(np.array(resize_image(
                                    Image.open(BytesIO(response.read())), 256).convert('RGB')), normalize='l1'), 15)))

                                if len(temp_histogram) > 0:
                                    histogram = temp_histogram

                            else:
                                raise Exception

                        else:
                            raise Exception

                    else:
                        raise Exception

                else:
                    raise Exception

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
                    query = query.filter(Media.categories.contains(categories))

                if types is not None and len(types) > 0:
                    query = query.filter(
                        or_(*list(map(lambda type: Media.type.like(f'{type}%'), types))))

                if usernames is not None and len(usernames) > 0:
                    query = query.filter(
                        or_(*list(map(lambda username: Media.username == username, usernames))))

                query = query.filter(Media.created_at >=
                                     datetime(1970, 1, 1, 0, 0, 0, 0))

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

                    media.append({
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
                    })

                return func.HttpResponse(json.dumps({'count': total_count, 'took': round(datetime.now(timezone.utc).timestamp() - start_time, 3), 'items': media}), status_code=200, mimetype='application/json', charset='utf-8')

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
