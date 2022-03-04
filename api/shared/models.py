from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_cns = Column(String(20))
    firstname = Column(String(20))
    lastname = Column(String(20))
    update_time = Column(DateTime)
    email = Column(String(128))
