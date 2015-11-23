# Date: 11/13/2015
# Author: Jack Chang (wei0831@gmail.com)

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    gplus_id = Column(String())
    username = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_updated = Column(DateTime(timezone=True),
                          server_default=func.now(), onupdate=func.now())


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_updated = Column(DateTime(timezone=True),
                          server_default=func.now(), onupdate=func.now())

    @property
    def serialize(self):
        return {
            "_id": self.id,
            "name": self.name
        }


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False, unique=True)
    description = Column(String(), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship(User)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_updated = Column(DateTime(timezone=True),
                          server_default=func.now(), onupdate=func.now())

    @property
    def serialize(self):
        return {
            "_id": self.id,
            "title": self.title,
            "description": self.description
        }

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
