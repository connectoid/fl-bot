from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, DateTime, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
 

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, nullable=False)
    is_scheduled = Column(Boolean, default = False)
    request_timeout = Column(Integer, default = 30)
    orders = relationship('Vacancy', backref='vacancies', lazy=True)
    links = relationship('CategoryLink', backref='category_links', lazy=True)

    def __repr__(self):
        return self.tg_id


class Vacancy(Base):
    __tablename__ = 'vacancy'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable = False)
    link = Column(String, nullable = False)
    is_favorite = Column(Boolean, default=False)
    is_new = Column(Boolean, default=True)
    date = Column(DateTime, default=datetime.now, nullable=False)
    owner = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return self.title


class CategoryLink(Base):
    __tablename__ = 'category_link'
    id = Column(Integer, primary_key=True)
    link = Column(String, nullable = False)
    owner = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return self.link