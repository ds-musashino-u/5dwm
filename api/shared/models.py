from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint, Integer, Float, String, Text, DateTime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer(), primary_key=True)
    name = Column('name', String(50))
    updated_at = Column('update_time', DateTime())


class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer(), primary_key=True)
    url = Column('file_name', Text())
    type = Column('kind', String(10))
    categories = Column('category', ARRAY(Text()))
    address = Column('place', Text())
    description = Column('description', Text())
    username = Column('user_cns', String(254))
    latitude = Column('lat', Float())
    longitude = Column('lng', Float())
    created_at = Column('datetaken', DateTime())
    vector = relationship('ImageVector', uselist=True)


class ImageVector(Base):
    __tablename__ = 'img_vector'
    id = Column('img_id', Integer(), ForeignKey('media.id'))
    feature = Column('feature', String(20))
    value = Column('val', Float())
    __table_args__ = (PrimaryKeyConstraint('img_id', 'feature', name='img_vector_pkey'),)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    username = Column('user_cns', String(254))
    first_name = Column('firstname', String(20))
    last_name = Column('lastname', String(20))
    updated_at = Column('update_time', DateTime())
    email = Column(String(254), default=None, nullable=True)


class MediaFile(Base):
    __tablename__ = 'csv_file'
    id = Column('csv_id', Integer(), primary_key=True)
    filename = Column('filename', Text())
    categories = Column('category', ARRAY(Text()))
    description = Column('description', Text())
    username = Column('user_cns', String(254))
    created_at = Column('datetaken', DateTime())
    updated_at = Column('update_time', DateTime())
    media_id = Column('media_id', Integer())


class MediaData(Base):
    __tablename__ = 'csv_info'
    file_id = Column('csv_id', Integer())
    id = Column('id', Integer())
    value = Column('value', Float())
    time = Column('date', DateTime())
    address = Column('location', Text())
    latitude = Column('lat', Float())
    longitude = Column('lon', Float())
    __table_args__ = (PrimaryKeyConstraint('csv_id', 'id', name='csv_info_pkey'), ForeignKeyConstraint(['csv_id'], ['csv_file.csv_id'], name="csv_info_csv_id_fkey", onupdate="CASCADE", ondelete="NO ACTION"))


class MediaFileEx(Base):
    __tablename__ = 'multi_csv_file'
    id = Column('csv_id', Integer(), primary_key=True)
    filename = Column('filename', Text())
    types = Column('data_types', ARRAY(Text()))
    categories = Column('category', ARRAY(Text()))
    description = Column('description', Text())
    username = Column('user_cns', String(254))
    created_at = Column('datetaken', DateTime())
    updated_at = Column('update_time', DateTime())
    media_id = Column('media_id', Integer())


class MediaDataEx(Base):
    __tablename__ = 'multi_csv_info'
    file_id = Column('csv_id', Integer())
    id = Column('id', Integer())
    values = Column('values', ARRAY(Float()))
    time = Column('date', DateTime())
    address = Column('location', Text())
    latitude = Column('lat', Float())
    longitude = Column('lon', Float())
    __table_args__ = (PrimaryKeyConstraint('csv_id', 'id'), ForeignKeyConstraint(['csv_id'], ['multi_csv_file.csv_id']))
