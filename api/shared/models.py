import os
#from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(os.environ.get('POSTGRESQL_CONNECTION_URL'), connect_args={'sslmode':'verify-full'}, pool_recycle=60)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'autoload': True}
    #id = Column(Integer, primary_key=True)
