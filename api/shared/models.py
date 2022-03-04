from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column('user_cns', String(20))
    first_name = Column('firstname', String(20))
    last_name = Column('lastname', String(20))
    updated_at = Column('update_time', DateTime)
    email = Column(String(128))
