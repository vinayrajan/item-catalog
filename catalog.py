#!/usr/bin/python

import os, random, string, datetime, json, httplib2, requests
import urllib.parse
from datetime import date
from datetime import datetime

from json import dumps
from urllib.parse import parse_qs

from flask import Flask, render_template, url_for, request, redirect, flash, json,jsonify, make_response,abort, g
from flask import session as user_session

from sqlalchemy import create_engine, asc, desc,text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_
from sqlalchemy import join
from sqlalchemy import func,Integer, Table, Column, MetaData
from sqlalchemy.sql import select,func



from dbsetup import *
from functools import wraps


from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError



# init new flask app
app = Flask(__name__)
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

#Database connection
engine = create_engine('sqlite:///itemcatalog.db',connect_args={'check_same_thread': False})
conn = engine.connect()
#Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()



# App routes
@app.route('/')
def showHome(): 
    categories = session.query(Category).order_by(asc(Category.category))
    products = session.query(Products).order_by(desc(Products.id))       
    return render_template('index.html',menu_categories = categories,products=products)

@app.route('/product-detail/<path:title>-<path:prod_id>.html')
def showProduct(title,prod_id):
    categories = session.query(Category).order_by(asc(Category.category))    
    
    sql_product = text('select * from products where id='+prod_id)
    result_product = session.execute(sql_product).fetchall()
    for rp in result_product:        
        cat=rp[5]    
    #cat_products = session.query(Products).filter(cat==cat ).order_by(desc(Products.id)).limit(3)         
    cat_products = session.query(Products).filter(Products.cat==cat).filter(Products.id != prod_id).order_by(desc(Products.id)).all()    
    return render_template('detail.html',menu_categories = categories,product=rp,related=cat_products)    

@app.route('/category/<path:name>-<path:id>.html')
def showCatalog(name,id):
    categories = session.query(Category).order_by(asc(Category.category)) 
    cat_products = session.query(Products).filter(Products.cat==id).order_by(desc(Products.id)).all()
    return render_template('category.html',menu_categories = categories,name=name,products=cat_products)

@app.route('/login.html')
def showLogin(): 
    categories = session.query(Category).order_by(asc(Category.category)) 
    return render_template('login.html',menu_categories = categories)

@app.route('/doGLogin', methods=['GET','POST'])
def doGLogin():
    if request.method == 'GET':
        # get posted data from Google
        if(request.args['id']):
            id=request.args['id']
            name=request.args['name']
            email=request.args['email']
            token=request.args['token']
            code=request.args['code']
            picture=request.args['picture']

            api_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
            now = datetime.now()
            dt_string = now.strftime("%Y-%b-%d %H:%M:%S")

            # check if request.form['id'] exists in Users table if exists get the id             
            result_user=session.query(Users).filter_by(gid=id).all()
                        
            if(result_user.count): 
                for row in result_user:                    
                    user_session['isuser'] = True                              
                    user_session['user_id'] = row.uid

            else:
                newUser = Users(
                    apikey=api_key,
                    fullname=request.args['name'],
                    email=request.args['email'],
                    gid=request.args['id'],
                    gtoken="",
                    gauth=dt_string                    
                )                    
                session.add(newUser)
                session.commit()

                user_session['isuser'] = True
                user = session.query(Users).filter_by(gid=id).one()
                user_session['user_id'] = user.uid 
                 
    return redirect(url_for('showHome')) 

    #if request.method == 'POST':
        # get posted data from Google
        
      

def authorize(us):
    @wraps(us)
    def x(*args, **kwargs):
        if 'isuser' not in user_session:                    
            return redirect('/login.html?login%20to%20procede')
        return us(*args, **kwargs)
    return x

@app.route("/logout.html")
def logout():    
    user_session.pop('isuser', None)
    user_session.pop('user_id')
    return render_template('logout.html')
    


# restricted to loged in users

@app.route("/profile.html", methods=['GET','POST'])
@authorize
def showprofile():
    userdetail=session.query(Users).filter_by(uid=user_session['user_id']).one()
    categories = session.query(Category).order_by(asc(Category.category))
    return render_template('profile.html',menu_categories = categories,user=userdetail)

@app.route("/managecategories.html", methods=['GET','POST','PUT','DELETE'])
@authorize
def manageCategories():    
    if request.method == 'GET':
        categories = session.query(Category).order_by(asc(Category.category)) 
        return render_template('managecategory.html',menu_categories = categories,categories = categories)
    if request.method == 'POST':
        # new category
        newCategory = Category(
            category=request.form['catname'],
            created_by=request.form['createdby'],
            created_on=date.today()
        )       
        session.add(newCategory)
        session.commit()

        categories = session.query(Category).order_by(asc(Category.category)) 
        flash("New Category called "+ request.form['catname'] + " Added")                
        return redirect(url_for('manageCategories'))

    if request.method == 'DELETE':
        id=request.form['id']
        catname=request.form['catname']
        
        deletethisrow = session.query(Category).filter_by(id=id).one()
        session.delete(deletethisrow)
        session.commit()

        categories = session.query(Category).order_by(asc(Category.category)) 
        #flash("The Category called "+ catname + " is Deleted")                
        #return redirect(url_for('manageCategories'))
        return "The Category called "+ catname + " is Deleted"

    if request.method == 'PUT':
        id=request.form['id']
        catname=request.form['catname']
        created_by=request.form['created_by']

        edithisrow = session.query(Category).filter_by(id=id).one()
        edithisrow.category = catname
        session.add(edithisrow)
        session.commit()
        return "updated"

@app.route("/manageproducts.html", methods=['GET','DELETE'])
@authorize
def manageProducts():
    if request.method == 'GET':
        categories = session.query(Category).order_by(asc(Category.category)) 
        products = session.query(Products, Category).join(Category).filter_by(created_by=user_session['user_id']).order_by(asc(Products.id))                                        
        return render_template('manageproduct.html',menu_categories = categories,products=products)

    if request.method == 'DELETE':
        id=request.form['prodid']
        title=request.form['prodtitle']
        
        deletethisrow = session.query(Products).filter_by(id=id).one()
        session.delete(deletethisrow)
        session.commit()
        return "The Product called "+ title + " is Deleted"

@app.route("/newproduct.html", methods=['GET','POST'])
@app.route("/editProduct/<path:name>-<path:id>.html", methods=['GET','POST'])
@authorize
def newProduct(id = None,name = None): 
    if request.method == 'GET':
        if(id):
           
            categories = session.query(Category).order_by(asc(Category.category)) 
            product=session.query(Products).filter_by(id=id).one()
            return render_template('newProduct.html',menu_categories = categories,product=product)     
        else:        
            categories = session.query(Category).order_by(asc(Category.category)) 
            return render_template('newproduct.html',menu_categories = categories,product="")

    if request.method == 'POST':
        if(request.form['prodid']):
                        
            id=request.form['prodid']            
            edithisrow = session.query(Products).filter_by(id=id).one()

            edithisrow.title=request.form['prodtitle']            
            edithisrow.description=request.form['proddesc']   
            edithisrow.price =request.form['prodprice']   
            edithisrow.pic1=request.form['prodpic1']   
            edithisrow.pic2 =request.form['prodpic2']   
            edithisrow.cat=request.form['prodcat']                      
            edithisrow.created_by = request.form['createdby']   
            edithisrow.created_on =  date.today()
                        
            session.add(edithisrow)           
            session.commit()

            categories = session.query(Category).order_by(asc(Category.category)) 
            flash("The Product "+ request.form['prodtitle'] + " has been updated")                
            return redirect(url_for('manageProducts'))
           
        else: 
            newProduct = Products(
                title=request.form['prodtitle'],            
                description=request.form['proddesc'],   
                price =request.form['prodprice'],   
                pic1=request.form['prodpic1'],   
                pic2 =request.form['prodpic2'],   
                cat=request.form['prodcat'],              
                is_active = 1,
                created_by = request.form['createdby'],   
                created_on =  date.today()
            )
            print(newProduct)
            session.add(newProduct)
            session.commit()

            categories = session.query(Category).order_by(asc(Category.category)) 
            flash("New Product  "+ request.form['prodtitle'] + " Added")                
            return redirect(url_for('manageProducts'))
#API
@app.route("/api/<path:api>", methods=['GET','POST','DELETE'])
def api(api = None):    
    #print(api)
    #print(request.args['key'])
    

    #?key=<path:apikey>
    
    if 'key' in request.args:
        
        apikey=request.args['key']
        # check if api key is a valid user
        user=session.query(Users).filter_by(apikey=apikey).all() 
        try:                    
            if(user[0]):
                createdby=user[0].uid                                       
                if api == "getProducts":
                    #items = session.query(Products).all() 
                    items = session.query(Products).filter_by(created_by=createdby).order_by(asc(Products.id))                                               
                    return jsonify(Products=[i.serialize for i in items])

                elif api == "getCategories":
                    items = session.query(Category).filter_by(created_by=createdby).all()
                    return jsonify(Categories=[i.serialize for i in items])
                else:
                    return jsonify({"code":"404","result":"Unknown API " + api})

            else:
                return jsonify({"code":"404","result":"Not a valid user"})
                
        except IndexError:
            return jsonify({"code":"404","result":"Not a valid user"})

    else:
        return jsonify({"code":"404","result":"API key not entered"})

def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# declaring a main function
if __name__ == '__main__':    
    app.debug = True
    app.secret_key = 'secretkey'
    app.run(host = '127.0.0.1', port = 5000)


