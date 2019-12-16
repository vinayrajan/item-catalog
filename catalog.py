import datetime
import random
import string
from datetime import date
from datetime import datetime
from functools import wraps

from flask import Flask
from flask import render_template, \
    url_for, \
    request, \
    redirect, \
    flash, \
    json, \
    jsonify
from flask import session as user_session
from sqlalchemy import asc, desc, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

import dbsetup

# from sqlalchemy import and_, or_
# from sqlalchemy import join
# from sqlalchemy import func, Integer, Table, Column, MetaData
# from sqlalchemy.sql import select, func

# from oauth2client.client import flow_from_clientsecrets
# from oauth2client.client import FlowExchangeError

# init new flask app
app = Flask(__name__)
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Database connection
engine = dbsetup.create_engine(
    'sqlite:///itemcatalog.db',
    connect_args={
        'check_same_thread': False})

# engine = dbsetup.create_engine(
#    'postgresql://catalog:password@localhost/catalog')
conn = engine.connect()
# Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# App routes
"""
Show Home function for the HomePage.
"""


@app.route('/')
def showHome():
    title = " Welcome to Catacart."
    categories = session.query(dbsetup.Category). \
        order_by(asc(dbsetup.Category.category))
    products = session.query(dbsetup.Products). \
        order_by(desc(dbsetup.Products.id))
    return render_template('index.html',
                           menu_categories=categories,
                           pagetitle=title,
                           products=products)


"""
Show Product function for displaying single product information.
takes in product id as a parameter
"""


@app.route('/product-detail/<path:title>-<path:product_id>.html')
def show_product(product_id, title=None):
    # global rp, cat
    # rp = []
    categories = session.query(dbsetup.Category) \
        .order_by(asc(dbsetup.Category.category))

    sql_product = text('select * from products where id=' + product_id)
    result_product = session.execute(sql_product).fetchall()
    for rp in result_product:
        cat = rp[6]
    cat_products = session.query(dbsetup.Products) \
        .filter(dbsetup.Products.cat == cat) \
        .filter(dbsetup.Products.id != product_id) \
        .order_by(desc(dbsetup.Products.id)).all()
    return render_template('detail.html',
                           menu_categories=categories,
                           pagetitle=title, product=rp,
                           related=cat_products)


"""
Show Catalog function for displaying products falling into a category.
takes in category id as a parameter
"""


@app.route('/category/<path:name>-<path:category_id>.html')
def showCatalog(category_id, name=None):
    title = name
    categories = session.query(dbsetup.Category) \
        .order_by(asc(dbsetup.Category.category))
    cat_products = session.query(dbsetup.Products) \
        .filter(dbsetup.Products.cat == category_id) \
        .order_by(desc(dbsetup.Products.id)).all()
    return render_template('category.html',
                           menu_categories=categories,
                           pagetitle=title, name=name,
                           products=cat_products)


"""
Function for displaying login page
"""


@app.route('/login.html')
def showLogin():
    categories = session.query(dbsetup.Category) \
        .order_by(asc(dbsetup.Category.category))
    return render_template('login.html',
                           pagetitle="Login Page",
                           menu_categories=categories)


"""
Function to handle logins through google.
the parameters of POST comes with a json of token and user profile info
"""


@app.route('/doGLogin', methods=['GET', 'POST'])
def doGLogin():
    if request.method == 'GET':
        # get posted data from Google
        if request.args['id']:
            id = request.args['id']
            name = request.args['name']
            email = request.args['email']
            token = request.args['token']
            code = request.args['code']
            picture = request.args['picture']

            api_key = ''.join(random.choice(
                string.ascii_uppercase + string.digits)
                for x in range(32))
            now = datetime.now()
            dt_string = now.strftime("%Y-%b-%d %H:%M:%S")

            # check if request.form['id'] exists in
            # Users table if exists get the id
            result_user = session.query(dbsetup.Users) \
                .filter_by(gid=id).all()

            if result_user.count:
                for row in result_user:
                    user_session['is_user'] = True
                    user_session['user_id'] = row.uid

            else:
                new_user = dbsetup.Users(
                    apikey=api_key,
                    fullname=request.args['name'],
                    email=request.args['email'],
                    gid=request.args['id'],
                    gtoken="",
                    gauth=dt_string
                )
                session.add(new_user)
                session.commit()

                user_session['is_user'] = True
                user = session.query(dbsetup.Users) \
                    .filter_by(gid=id).one()
                user_session['user_id'] = user.uid

    return redirect(url_for('showHome'))

    # if request.method == 'POST':
    # get posted data from Google


def authorize(us):
    @wraps(us)
    def x(*args, **kwargs):
        if 'is_user' not in user_session:
            return redirect('/login.html?login-to-proceed')
        return us(*args, **kwargs)

    return x


"""
Function to handle logout
"""


@app.route("/logout.html")
def logout():
    user_session.pop('is_user', None)
    user_session.pop('user_id')
    return render_template('logout.html')


# restricted to logged in users
"""
Function to handle user profile page
needs the user session
"""


@app.route("/profile.html", methods=['GET', 'POST'])
@authorize
def show_profile():
    user_detail = session.query(dbsetup.Users) \
        .filter_by(uid=user_session['user_id']).one()
    categories = session.query(dbsetup.Category) \
        .order_by(asc(dbsetup.Category.category))
    return render_template('profile.html',
                           pagetitle="Profile and Help",
                           menu_categories=categories, user=user_detail)


"""
Function to manage the categories as an administrator
"""


@app.route("/managecategories.html", methods=['GET', 'POST', 'PUT', 'DELETE'])
@authorize
def manage_categories():
    if request.method == 'GET':
        categories = session.query(dbsetup.Category) \
            .order_by(asc(dbsetup.Category.category))
        return render_template('managecategory.html',
                               pagetitle="Manage Categories",
                               menu_categories=categories,
                               categories=categories)
    if request.method == 'POST':
        # new category
        new_category = dbsetup.Category(
            category=request.form['catname'],
            created_by=request.form['createdby'],
            created_on=date.today()
        )
        session.add(new_category)
        session.commit()

        categories = session.query(dbsetup.Category) \
            .order_by(asc(dbsetup.Category.category))
        flash("New Category called " + request.form['catname'] + " Added")
        return redirect(url_for('manage_categories'))

    if request.method == 'DELETE':
        category_id = request.form['id']
        category_name = request.form['catname']

        delete_this_row = session.query(dbsetup.Category) \
            .filter_by(id=category_id).one()
        session.delete(delete_this_row)
        session.commit()

        categories = session.query(dbsetup.Category) \
            .order_by(asc(dbsetup.Category.category))
        # flash("The Category called "+ category_name + " is Deleted")
        # return redirect(url_for('manageCategories'))
        return "The Category called " + category_name + " is Deleted"

    if request.method == 'PUT':
        product_id = request.form['id']
        category_name = request.form['catname']
        created_by = request.form['created_by']

        edit_this_row = session.query(dbsetup.Category) \
            .filter_by(id=product_id).one()
        edit_this_row.category = category_name
        session.add(edit_this_row)
        session.commit()
        return "updated"


"""
Function to products the categories as an administrator
"""


@app.route("/manageproducts.html", methods=['GET', 'DELETE'])
@authorize
def manage_products():
    if request.method == 'GET':
        categories = session.query(dbsetup.Category) \
            .order_by(asc(dbsetup.Category.category))

        products = session.query(dbsetup.Products, dbsetup.Category) \
            .join(dbsetup.Category) \
            .order_by(asc(dbsetup.Products.id))
        # .filter_by(created_by=user_session['user_id']) \

        print(products)

        return render_template('manageproduct.html',
                               pagetitle="Manage Products",
                               menu_categories=categories,
                               products=products)

    if request.method == 'DELETE':
        product_id = request.form['prodid']
        product_title = request.form['prodtitle']

        delete_this_row = session.query(dbsetup.Products) \
            .filter_by(id=product_id).one()
        session.delete(delete_this_row)
        session.commit()
        return "The Product called " + product_title + " is Deleted"


"""
Function to  add a new product as an administrator
"""


@app.route("/newproduct.html", methods=['GET', 'POST'])
@app.route("/editProduct/<path:name>-<path:product_id>.html",
           methods=['GET', 'POST'])
@authorize
def newProduct(product_id=None, name=None):
    if request.method == 'GET':
        if product_id:

            categories = session.query(dbsetup.Category) \
                .order_by(asc(dbsetup.Category.category))
            product = session.query(dbsetup.Products) \
                .filter_by(id=product_id).one()
            return render_template('newproduct.html',
                                   pagetitle="Add a new Product",
                                   menu_categories=categories,
                                   product=product)
        else:
            categories = session.query(dbsetup.Category) \
                .order_by(asc(dbsetup.Category.category))
            return render_template('newproduct.html',
                                   pagetitle="Add a new Product",
                                   menu_categories=categories,
                                   product="")

    if request.method == 'POST':
        if request.form['prodid']:

            product_id = request.form['prodid']
            product_title = request.form['prodtitle']
            edit_this_row = session.query(dbsetup.Products) \
                .filter_by(id=product_id).one()

            edit_this_row.title = request.form['prodtitle']
            edit_this_row.description = request.form['proddesc']
            edit_this_row.price = request.form['prodprice']
            edit_this_row.pic1 = request.form['prodpic1']
            edit_this_row.pic2 = request.form['prodpic2']
            edit_this_row.cat = request.form['prodcat']
            edit_this_row.created_by = request.form['createdby']
            edit_this_row.created_on = date.today()

            session.add(edit_this_row)
            session.commit()

            # categories = session.query(dbsetup.Category) \
            #     .order_by(asc(dbsetup.Category.category))
            flash("The Product " + product_title + " has been updated")
            return redirect(url_for('manage_products'))

        else:
            new_product = dbsetup.Products(
                title=request.form['prodtitle'],
                description=request.form['proddesc'],
                price=request.form['prodprice'],
                pic1=request.form['prodpic1'],
                pic2=request.form['prodpic2'],
                cat=request.form['prodcat'],
                is_active=1,
                created_by=request.form['createdby'],
                created_on=date.today()
            )
            # print(newProduct)
            session.add(new_product)
            session.commit()
            flash("New Product  " + request.form['prodtitle'] + " Added")
            return redirect(url_for('manage_products'))


def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}


"""
API Function to  get all the products
"""


@app.route("/products/json")
def all_product_json():
    items = session.query(dbsetup.Products).order_by(asc(dbsetup.Products.id))
    # return jsonify(Products=[i.serialize for i in items])
    products = [i.serialize for i in items]
    if len(products) > 0:
        return jsonify(products)
    else:
        return jsonify({404: "No category found"})


"""
API Function to  get all the categories
"""


@app.route("/categories/json")
def all_categories_json():
    items = session.query(dbsetup.Category).order_by(asc(dbsetup.Category.id))
    # return jsonify(Category=[i.serialize for i in items])]
    category = [i.serialize for i in items]
    if len(category) > 0:
        return jsonify(category)
    else:
        return jsonify({404: "No category found"})


"""
API Function to  get a single product
"""


@app.route("/product/<int:product_id>/json")
def one_product_json(product_id):
    # product_id = request.args['product_id']
    items = session.query(dbsetup.Products) \
        .filter_by(id=product_id) \
        .order_by(asc(dbsetup.Products.id))

    products = [i.serialize for i in items]
    if len(products) > 0:
        return jsonify(products)
    else:
        return jsonify({404: "No products found"})


"""
API Function to  get a single category
"""


@app.route("/category/<int:category_id>/json")
def one_category_json(category_id):
    # category_id = request.args['category_id']
    items = session.query(dbsetup.Category).filter_by(id=category_id) \
        .order_by(asc(dbsetup.Category.id))
    # return jsonify(Category=[i.serialize for i in items])
    category = [i.serialize for i in items]
    if len(category) > 0:
        return jsonify(category)
    else:
        return jsonify({404: "No Category found"})


# declaring a main function
if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'secretkey'
    app.run()
    # app.run(host='0.0.0.0')
