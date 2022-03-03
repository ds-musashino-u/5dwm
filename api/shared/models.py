from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'autoload': True}
    #id = Column(Integer, primary_key=True)

    def __init__(self):
        pass