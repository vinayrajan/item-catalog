#!/usr/bin/python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dbsetup import Base, Products, Category, Users

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

user_actor = [
    Users(uid="0", apikey="A51PP404HQ6TDWFNXG6UTA76OPHJCE6Q", fullname="Vinay Kumar Rajan",
          email="rajan.vinay@gmail.com", gid="111982684779264334126", gtoken="", gauth="")
]

cat_objects = [
    Category(category="Mens Shirts", created_by="0", created_on="2019/10/10"),
    Category(category="Women's Shirts", created_by="0", created_on="2019/10/10"),
    Category(category="Mens Pants", created_by="0", created_on="2019/10/10"),
    Category(category="Women's Pants", created_by="0", created_on="2019/10/10"),
    Category(category="Mens Accessories", created_by="0", created_on="2019/10/10"),
    Category(category="Women's Accessories", created_by="0", created_on="2019/10/10"),
]

prod_objects = [
    Products(title="Women's Blouse", description="Women's Blouse", price="16.00",
             pic1="http://bestjquery.com/tutorial/product-grid/demo9/images/img-1.jpg",
             pic2="http://bestjquery.com/tutorial/product-grid/demo9/images/img-2.jpg", cat="2", rating="4.5",
             is_active="1", created_by="0", created_on="2019/10/10"),
    Products(title="Men's Plain Tshirt", description="Men's Plain Tshirt", price="5.00",
             pic1="http://bestjquery.com/tutorial/product-grid/demo9/images/img-3.jpg",
             pic2="http://bestjquery.com/tutorial/product-grid/demo9/images/img-4.jpg", cat="1", rating="3",
             is_active="1", created_by="0", created_on="2019/10/10"),
    Products(title="Men's Plain Tshirt", description="Men's Plain Tshirt", price="15.00",
             pic1="http://bestjquery.com/tutorial/product-grid/demo9/images/img-5.jpg",
             pic2="http://bestjquery.com/tutorial/product-grid/demo9/images/img-6.jpg", cat="1", rating="3.2",
             is_active="1", created_by="0", created_on="2019/10/10"),
    Products(title="Women's Plain Tshirt", description="Women's Plain Tshirt", price="22.00",
             pic1="http://bestjquery.com/tutorial/product-grid/demo9/images/img-7.jpg",
             pic2="http://bestjquery.com/tutorial/product-grid/demo9/images/img-8.jpg", cat="1", rating="4",
             is_active="1", created_by="0", created_on="2019/10/10"),
]

session.bulk_save_objects(user_actor)
session.bulk_save_objects(cat_objects)
session.bulk_save_objects(prod_objects)
session.commit()

print("added categories, added sample products!")
