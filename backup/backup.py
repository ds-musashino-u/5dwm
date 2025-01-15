import math
import os
import json
from datetime import datetime, MINYEAR
from urllib.parse import urlparse
from dotenv import load_dotenv
from tqdm.auto import tqdm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Media
from azure.storage.blob import BlobServiceClient


load_dotenv(verbose=False)


AZURE_STORAGE_CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']


engine = create_engine(os.environ['POSTGRESQL_CONNECTION_URL'], connect_args={'sslmode': 'require'}, pool_recycle=60)
media_items = []

backup_directory = os.environ.get('BACKUP_DIRECTORY', 'Media')
today = datetime.today().strftime('%Y%m%d')
media_data_directory = os.path.join(backup_directory, today)
os.makedirs(media_data_directory, exist_ok=True)


def download(url, container_name = 'media'):
    path =  os.path.basename(urlparse(item['url']).path)
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(path)

    if blob_client.exists():
        content_type = blob_client.get_blob_properties().content_settings.content_type
        metadata = blob_client.get_blob_properties().metadata
        output_media_path = os.path.join(media_data_directory, path)

        if not os.path.exists(output_media_path):
            with open(output_media_path, mode="wb") as file:
                download_stream = blob_client.download_blob()
                file.write(download_stream.readall())
            
        return content_type, metadata
    
    return None, None


try:
    limit = 100
    Session = sessionmaker(bind=engine)
    session = Session()
    query = session.query(Media)
    query = query.filter(Media.created_at >= datetime(MINYEAR, 1, 1, 0, 0, 0, 0))
    query = query.order_by(Media.id)
    total_count = float(query.count())

    query = query.limit(limit)

    with tqdm(range(math.ceil(total_count / limit))) as pbar:
        for i in pbar:
            for item in query.offset(i * limit).all():
                if item.url.lower().startswith('https://static.5dworldmap.com/'):                    
                    media_items.append({'id': item.id, 'url': item.url})

finally:
    session.close()


with tqdm(media_items) as pbar:
    for item in pbar:
        content_type, metadata = download(item['url'])
        item['content_type'] = content_type
        item['metadata'] = metadata

        pbar.set_description(item['url'])


with open(os.path.join(backup_directory, f'{today}.jsonl'), 'w') as file:
    for item in media_items:
        file.write(f'{json.dumps(item)}\n')
