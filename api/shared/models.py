from sqlalchemy import Column, Integer, Float, String, Text, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base

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
    username = Column('user_cns', String(20))
    latitude = Column('lat', Float())
    longitude = Column('lng', Float())
    created_at = Column('datetaken', DateTime())


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    username = Column('user_cns', String(20))
    first_name = Column('firstname', String(20))
    last_name = Column('lastname', String(20))
    updated_at = Column('update_time', DateTime())
    email = Column(String(128), default=None, nullable=True)
