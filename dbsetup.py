#!/usr/bin/python

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base,DeclarativeMeta
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy import Sequence
 
Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    uid = Column(Integer, Sequence('u_id_seq'), primary_key=True )
    apikey = Column(String(250), nullable=False)
    fullname = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    gid = Column(String(250), nullable=False)
    gtoken = Column(String(250), nullable=False)
    gauth = Column(String(250), nullable=False)

    @property
    def serialize(self):      
       return {
           'apikey': self.apikey,
           'uid': self.uid,
           'fullname': self.fullname,
           'email':self.email,
           'gid': self.gid,
           'gtoken': self.gtoken,
           'gauth':self.gauth,
       }

class Category(Base):
    __tablename__ = 'category'
   
    id = Column(Integer, Sequence('cat_id_seq'), primary_key=True )
    category = Column(String(250), nullable=False)
    created_by= Column(Integer,ForeignKey('users.uid'))
    created_on=  Column(String(250), nullable=False)

    @property
    def serialize(self):      
       return {
           'category': self.category,
           'id': self.id,
           'created_by': self.created_by,
           'created_on':self.created_on
       }
 

class Products(Base):
    __tablename__ = 'products'
   
    id = Column(Integer, Sequence('prod_id_seq'), primary_key=True)
    title = Column(String(250))
    description = Column(String(250))
    price = Column(String(10))
    pic1 = Column(String(250), nullable=False)
    pic2 = Column(String(250), nullable=False)
    cat	= Column(Integer,ForeignKey('category.id'))
    rating = Column(Integer)
    is_active = Column(Integer)
    created_by = Column(Integer,ForeignKey('users.uid'))
    created_on =  Column(String(250), nullable=False)
    

    @property
    def serialize(self):       
       return {           
            'id':self.id,
            'title':self.title,
            'description':self.description,
            'price':self.price,
            'pic1':self.pic1,
            'pic2':self.pic2,
            'cat':self.cat,
            'rating':self.rating,
            'is_active':self.is_active,
            'created_by': self.created_by,
            'created_on':self.created_on
       } 

engine = create_engine('sqlite:///itemcatalog.db',connect_args={'check_same_thread': False})


Base.metadata.create_all(engine)      

print("Database created, to load sample data run `python sampledata.py`!")