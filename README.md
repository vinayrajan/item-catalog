
# Project: Item Catalog

 Item Catalog is a project in the Full Stack Web Developer Nanodegree Program, This project works on RESTful web application using the Python, Flask, OAuth2 & Sqlalchemy. 
 
# Project Overview
 The Project Item Catalog is a collection of products and categories on the webpage. The homepage shows the products in the database. The category page shows the products for the category.
 There is a login page that uses OAuth2 from Google. Once logged in the user can add and customize his products.

The project uses the following modules

  - flask (https://pypi.org/project/Flask/)
  - sqlalchemy (https://www.sqlalchemy.org/)
  - datetime
  - urllib
  - oauth2client

The webpage uses the following components
- jquery 3.2.1 (https://jquery.com/)
- Bootstrap 4 (https://getbootstrap.com/)
- font-awesome 4.7.0 (https://fontawesome.com/v4.7.0/)


### Installation

Log Analysis requires [Python](https://www.python.org/) v3.6+ to run.

To install modules try ```pip install <module name>``` or ```pip  install  -r  requirements.txt```



If you want to setup the db with the sample data 

```sh
python3 sampledata.py
```

If you want to setup the db without the sample data 

```sh
$ python3 dbsetup.py
```

the console output would be similar to...

```sh
 * Database created, to load sample data run `python sampledata.py`!
 * added categories, added sample products!
```
and finally run 
```sh
$ python3 catalog.py
Database created, to load sample data run `python sampledata.py`!
 * Serving Flask app "catalog" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Restarting with stat
Database created, to load sample data run `python sampledata.py`!
 * Debugger is active!
 * Debugger PIN: 324-895-452
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
The app is now running on the localhost and port 5000.

### Checking the output on browser

Open your  browser and hit the url [localhost](http://localhost:5000).

#### Homepage

You should be able to see the sample products on the home page. 
- The header should be having the catacart logo
- Home link, and a categories drop down.
- The header also has a login button for the users who have not logged in.
-  A welcome message   for the users who have logged in.
- A drop down menu for administration section to access profile, manage products page, manage categories page and a link to logout.

From the home page if you click on the [View this Product](http://localhost:5000/product-detail/Women%27s%20Plain%20Tshirt-4.html) link under the product pic the page is navigated to the detail page.
the detail page also contains all the products listed under the category under the section related products

From the homepage menu if you click the links on the category drop down the page will be navigated to  category page where you can find all the products listed under the category.

#### Administration 

> Only for the logged in users
 
Manage Category 
Opens the category page with a table containing the Id, Category Name and Actions that will have link to edit and delete the category.
Adding a new category is managed under the table and it is validated using the jquery validation plugin

Manage Products
This link opens up a page containing products added by the user. The table shows product information with edit and delete buttons. 
The new product requires
1. Product Title
2. Product Picture 1
3. Product Picture 2
4. Product Description
5. Product Category
6. Product Price


 
#### Profile
> Only for the logged in users

1. The profile page shows the information about the logged in user.
2. The API Key section gives you the API key that can be used to get data from  API in the JSON format
3. The  API Usage section provides the help to use the API. It includes the common success and failure messages.
4. The settings section is right now blank.

#### API
The api section are a set of functions that return JSON objects of the requested data

Api example:
- [GET] http://localhost:5000/categories/json
- [GET] http://localhost:5000/products/json
- [GET] http://localhost:5000/product/{Product-ID}/json 
    * example: http://localhost:5000/product/1/json
- [GET] http://localhost:5000/category/{Category-ID}/json 
    * example: http://localhost:5000/category/1/json
    
Thankyou
Vinay Kumar Rajan
vr3924@intl.att.com
