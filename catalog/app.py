# Date: 11/13/2015
# Author: Jack Chang (wei0831@gmail.com)
import random
import string
from functools import wraps

# Flask framework
from flask import Flask, render_template
from flask import redirect, request, make_response
from flask import session, flash
from flask import url_for
from flask import jsonify
from flask.ext.seasurf import SeaSurf

# SQLite
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

# Database Schemas
from database_setup import Base, User, Category, Item

# Oauth
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

# XNL
from dicttoxml import dicttoxml

# Falsk App
app = Flask(__name__)
csrf = SeaSurf(app)
app.secret_key = ''.join(
    random.choice(string.ascii_uppercase+string.digits) for x in xrange(32))

# Dabasbase Session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
db = sessionmaker(bind=engine)()

# Oauth2
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Simple Catalog"


# Helper functions
def redirect_url(default='index'):
    '''
    Tries to redirect to previous page
    '''
    return request.args.get('next') or \
        request.referrer or \
        url_for(default)


def login_required(f):
    '''
    View decorator function making sure only login user can access the page
    '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('gplus_id') is None:
            return redirect(redirect_url())
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    '''
    Render index page with categories and latest items
    '''
    # All Category
    categories = db.query(Category).all()
    # Latest Items
    items = db.query(Item).order_by(desc(Item.date_updated))
    return render_template("index.html",
                           APPLICATION_NAME=APPLICATION_NAME,
                           categories=categories,
                           items=items)


@app.route('/catalog.json')
def showCatalogJson():
    '''
    Provide JSON endpoints for all catalog itemss
    '''
    # First, store all categories
    categories = db.query(Category).all()
    result = {"Category": [c.serialize for c in categories]}

    # Next, push items into coresponding category
    items = db.query(Item).order_by(asc(Item.category_id))
    for i in items:
        if 'items' not in result['Category'][i.category_id]:
            result['Category'][i.category_id]['items'] = []

        result['Category'][i.category_id]['items'].append(i.serialize)

    response = make_response(jsonify(result), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/catalog.xml')
def showCatalogXML():
    '''
    Provide XML endpoints for all catalog itemss
    '''
    # First, store all categories
    categories = db.query(Category).all()
    result = {"Category": [c.serialize for c in categories]}

    # Next, push items into coresponding category
    items = db.query(Item).order_by(asc(Item.category_id))
    for i in items:
        if 'items' not in result['Category'][i.category_id]:
            result['Category'][i.category_id]['items'] = []

        result['Category'][i.category_id]['items'].append(i.serialize)

    response = make_response(dicttoxml(result), 200)
    response.headers['Content-Type'] = 'application/xml'
    return response


@app.route('/catalog/add', methods=['GET', 'POST'])
@login_required
def addItem():
    '''
    GET: Render Add Item paage
    POST: Add Item (title, description, category, user_id) into database
    '''
    if request.method == 'POST':
        newitem = Item(title=request.form['title'],
                       description=request.form['description'],
                       category_id=request.form['category_id'],
                       user_id=session['user_id'])
        db.add(newitem)
        db.commit()
        return redirect(url_for('index'))
    else:
        categories = db.query(Category).all()
        return render_template("additem.html",
                               APPLICATION_NAME=APPLICATION_NAME,
                               categories=categories)


@app.route('/catalog/<string:category_name>/add', methods=['GET', 'POST'])
@login_required
def addCategoryItem(category_name):
    '''
    GET: Render Add Item page with given category
    POST: Add Item (title, description, category, user_id) into database
    '''
    if request.method == 'POST':
        newitem = Item(title=request.form['title'],
                       description=request.form['description'],
                       category_id=request.form['category_id'],
                       user_id=session['user_id'])
        db.add(newitem)
        db.commit()
        return redirect(url_for('index'))
    else:
        categories = db.query(Category).all()
        return render_template("additem.html",
                               APPLICATION_NAME=APPLICATION_NAME,
                               categories=categories,
                               current_category=category_name)


@app.route('/catalog/<string:category_name>/<string:item_name>/edit',
           methods=['GET', 'POST'])
@login_required
def editItem(category_name, item_name):
    '''
    GET: Render Edit Item page with given category and item name
    POST: Update Item (title, description, category, user_id) in database
    '''
    # Prevent from user gussing url or incorrect url
    try:
        category = db.query(Category).filter_by(name=category_name).one()
    except:
        return redirect(url_for('index'))
    # Prevent from user gussing url or incorrect url
    try:
        item = db.query(Item).filter_by(category_id=category.id,
                                        title=item_name).one()
    except:
        return redirect(url_for('index'))
    # Only owner of the item can edit
    if item.user_id != session['user_id']:
        return redirect(url_for('index'))

    if request.method == 'POST':
        db.query(Item).filter_by(category_id=category.id, title=item_name).\
            update({Item.title: request.form['title'],
                    Item.description: request.form['description'],
                    Item.category_id: request.form['category_id']})
        db.commit()

        return redirect(url_for('index'))

    else:
        categories = db.query(Category).all()
        return render_template("edititem.html",
                               APPLICATION_NAME=APPLICATION_NAME,
                               item=item,
                               categories=categories)


@app.route('/catalog/<string:category_name>/<string:item_name>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteItem(category_name, item_name):
    '''
    GET: Render Delete Item page with given category and item name
    POST: Delete Item (title, description, category, user_id) in database
    '''
    # Prevent from user gussing url or incorrect url
    try:
        category = db.query(Category).filter_by(name=category_name).one()
    except:
        return redirect(url_for('index'))

    # Prevent from user gussing url or incorrect url
    try:
        item = db.query(Item).filter_by(category_id=category.id,
                                        title=item_name).one()
    except:
        return redirect(url_for('index'))

    # Only owner of the item can delete
    if item.user_id != session['user_id']:
        return redirect(url_for('index'))

    if request.method == 'POST':
        db.query(Item).filter_by(category_id=category.id, title=item_name).\
            delete(synchronize_session='evaluate')
        db.commit()
        return redirect(url_for('index'))
    else:
        categories = db.query(Category).all()
        return render_template("deleteitem.html",
                               APPLICATION_NAME=APPLICATION_NAME,
                               item=item,
                               categories=categories)


@app.route('/catalog/<string:category_name>/<string:item_name>')
def showItem(category_name, item_name):
    '''
    GET: Render Show Item page with given category and item name
    '''
    # Prevent from user gussing url or incorrect url
    try:
        category = db.query(Category).filter_by(name=category_name).one()
    except:
        return redirect(url_for('index'))

    # Show all items under this category
    if item_name == 'items':
        categories = db.query(Category).all()
        items = db.query(Item).filter_by(category_id=category.id).\
            order_by(desc(Item.date_updated))
        return render_template("showcategory.html",
                               APPLICATION_NAME=APPLICATION_NAME,
                               current_category=category_name,
                               categories=categories,
                               items=items)
    else:
        # Prevent from user gussing url or incorrect url
        try:
            item = db.query(Item).filter_by(category_id=category.id,
                                            title=item_name).one()
        except:
            return redirect(url_for('index'))
        return render_template("showitem.html",
                               APPLICATION_NAME=APPLICATION_NAME,
                               item=item)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''
    POST: Talk to google sever and get user info
    '''
    code = request.data

    # Check authorization code
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = "postmessage"
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = session.get('credentials')
    stored_gplus_id = session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
                   json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['credentials'] = credentials.to_json()
    session['gplus_id'] = gplus_id

    # check if user with given gplus_id already exist in database
    try:
        user = db.query(User).filter_by(gplus_id=gplus_id).one()
    except:
        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()
        # if not found in database, create a new user recording the info
        user = User(gplus_id=gplus_id,
                    username=data['name'],
                    email=data['email'],
                    picture=data['picture'])
        db.add(user)
        db.commit()

    # Store user info in session
    session['username'] = user.username
    session['picture'] = user.picture
    session['email'] = user.email
    session['user_id'] = user.id

    return redirect(url_for('index'))


@app.route("/gdisconnect")
def gdisconnect():
    '''
    POST: Talk to google sever and disconnect user
    '''
    credentials = session.get('credentials')
    if credentials is None:
        return None

    # Check if access_token is valid
    access_token = json.loads(credentials)['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result is None:
        return redirect(url_for('index'))
    elif result['status'] == '200':
        del session['credentials']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['picture']
        del session['user_id']
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))
        
if __name__ == '__main__':
    app.run()
