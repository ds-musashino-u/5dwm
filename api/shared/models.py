import os
#from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

#meta = Metadata(engine)
#meta.reflect()
#Base = declarative_base(metadata=meta)

class User():
    __tablename__ = 'users'
    __table_args__ = {'autoload': True}
    #id = Column(Integer, primary_key=True)
