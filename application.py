#!/usr/bin/env python
"""
Udacity Item Catalog Project

Author: Efren Aguilar

Python Version 3.7.2 used when created

This module is used to run the main Flask application
for this project. A Item Catalog website with the
ability to peform CRUD operations on a database
for Items within various Categories, the ability
to sign in via a Google Account, and the ability
to access data via basic JSON API endpoints
"""

from flask import Flask, render_template
from flask import request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databaseSetup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps


app = Flask(__name__)

secrets_file = "client_secrets.json"
CLIENT_ID = json.loads(open(secrets_file, "r").read())["web"]["client_id"]
APPLICATION_NAME = "Item Catalog"

db = "sqlite:///itemCatalog.db"
engine = create_engine(db, connect_args={"check_same_thread": False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# BEGIN HELPER FUNCTIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" in login_session:
            return f(*args, **kwargs)
        else:
            return redirect("/login")
    return decorated_function

def createUser(login_session):
    """Given a login_session (flask session) object, creates a new user
    with the data and adds it to the User database

    Args:
            login_session (flask session): The flask session object

    Returns:
            The user id of the newly created user
    """
    newUser = User(name=login_session["username"],
                   email=login_session["email"],
                   picture=login_session["picture"])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session["email"]).one()
    return user.id


def getUserInfo(user_id):
    """Given a user_id, obtains the user's data from the database

    Args:
            user_id (int): The user_id to get info for

    Returns:
            The User object with a matching user_id. None if none found
    """
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except:
        return None


def getUserId(email):
    """Given an email address, obtain the user_id for that email

    Args:
            email (str): The email address of the user

    Returns:
            The user id with a matching email address. None if none found
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getAllCategories():
    """Returns all the categories within the database

    Returns:
            A list containing all of the Category objects within the database
    """
    categories = session.query(Category).all()
    return categories


def getCategory(category_name):
    """Given a category_name, obtain the category object for that name

    Args:
            category_name (str): The name of the category

    Returns:
            The Category object with a matching name. None if none found
    """
    try:
        category = session.query(Category).filter_by(name=category_name).one()
        return category
    except:
        return None


def getItem(category, item_title):
    """Given a category and item_title, returns the
    Item with a matching category and title

    Args:
            category (Category): The category to look for this Item in
            item_title (str): The title of the item

    Returns:
            The Item object with a matching category and title.
            None if none found
    """
    try:
        item = session.query(Item).filter_by(
            cat_id=category.id, title=item_title).one()
        return item
    except:
        return None


def getAllItemsInCategory(category):
    """Given a category, returns a list of all the Item objects in that category

    Args:
            category (Category): The category to get Items from

    Returns:
            A list of all the Item objects within this Category
    """
    cat_items = session.query(Item).filter_by(cat_id=category.id).all()
    return cat_items


def addSerializedItemsToCategory(category):
    """Given a category, serializes all the items within the
    category and adds them to the serialized version
    of the category. Returns this master serialization

    Args:
            category (Category): The Category to add serialized Items to

    Returns:
            A serialized Category containing all of its Serialized Items
    """
    catSerialized = category.serialize
    cat_items = getAllItemsInCategory(category)
    if len(cat_items) > 0:
        catSerialized["Item"] = [i.serialize for i in cat_items]
    return catSerialized


def JSONDumpsResponse(responseStr, code):
    """Given a string and response code, creates a json.dumps style
    response with the response code

    Args:
            response (str): The message to send in the response
            code (int): The response code to send with the response

    Returns:
            A flask make_response object with the given parameters
    """
    response = make_response(json.dumps("responseStr"), code)
    response.headers["Content-Type"] = "application/json"
    return response


def isUniqueTitle(cat_id, title):
    """Given a title and a category, checks to see if that title is
    unique in that category

    Args:
            cat_id (int): The id of the category to check
            title (str): The title to check for uniqueness
    """
    category = session.query(Category).filter_by(id=cat_id).one()
    itemTitles = [i.title for i in getAllItemsInCategory(category)]
    if title in itemTitles:
        return False
    return True

# END HELPER FUNCTIONS


@app.route("/catalog.json")
def catalogJSON():
    """Returns a jsonified representation of the entire Category/Item dataset
    """
    categories = getAllCategories()
    serializedCategories = []
    for category in categories:
        catSerialized = addSerializedItemsToCategory(category)
        serializedCategories.append(catSerialized)
    return jsonify(Category=[c for c in serializedCategories])


@app.route("/catalog/<string:category_name>.json")
def categoryJSON(category_name):
    """Returns a jsonified representation of a given category

    Args:
            category_name (str): The name of the category to serialize
    """
    category = getCategory(category_name)
    if category is None:
        return ("Category {} not found").format(category_name)
    catSerialized = addSerializedItemsToCategory(category)
    return jsonify(catSerialized)


@app.route("/catalog/<string:category_name>/<string:item_title>.json")
def itemJson(category_name, item_title):
    """Returns a jsonified representation of a given item

    Args:
            category_name (str): The name of the category the item is in
            item_title (str): The title of the item to serialize
    """
    category = getCategory(category_name)
    if category is None:
        return ("Category {} not found").format(category_name)
    item = getItem(category, item_title)
    if item is None:
        return ("Item {} not found").format(item_title)
    return jsonify(item.serialize)


@app.route("/login")
def showLogin():
    """Generates a random state token and renders the login page
    """
    state = "".join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session["state"] = state
    return render_template("login.html", STATE=state)


@app.route("/gconnect", methods=["POST"])
def gconnect():
    """Tries to login a user via a Google account
    Raises any appropriate errors if there were any
    during the exchange of information
    """
    # Validate state token
    if request.args.get("state") != login_session["state"]:
        return JSONDumpsResponse("Invalid state parameter", 401)
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object

        # Creates oauth_flow object and adds client_secret key info to it
        oauth_flow = flow_from_clientsecrets("client_secrets.json", scope="")
        # Specifies this is the one time code verification being sent by server
        oauth_flow.redirect_uri = "postmessage"
        # Intiates the exchange, passing the one time code as input
        # Exchanges an authorization code for a credentials object
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return JSONDumpsResponse("Failed to upgrade the authorization code",
                                 401)

    # Given a credentials object, check that the access token is valid
    access_token = credentials.access_token
    # The following url will verify if the given token is valid for use
    url = "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}"
    url = (url).format(access_token)
    # Create a JSON get request containing the url and access token
    h = httplib2.Http()
    result = json.loads(h.request(url, "GET")[1])

    # If there was an error in the access token info, abort.
    if result.get("error") is not None:
        return JSONDumpsResponse(result.get("error"), 500)

    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token["sub"]
    if result["user_id"] != gplus_id:
        return JSONDumpsResponse("Token's user ID doesn't match given user ID",
                                 401)

    # Verify that the the access token is valid for this app
    if result["issued_to"] != CLIENT_ID:
        return JSONDumpsResponse("Token's client ID does not match app's", 401)

    # Check to see if the user has already been logged in
    stored_access_token = login_session.get("access_token")
    stored_gplus_id = login_session.get("gplus_id")
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        return JSONDumpsResponse("Current user is already connected", 200)

    # Store the access token in the session for later use
    login_session["access_token"] = credentials.access_token
    login_session["gplus_id"] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {"access_token": credentials.access_token, "alt": "json"}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    try:
        login_session["username"] = data["name"]
    except:
        login_session["username"] = data["email"]
    login_session["picture"] = data["picture"]
    login_session["email"] = data["email"]

    # See if user exists, if it doesn't make a new one
    user_id = getUserId(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session["user_id"] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150'
    output += 'px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash(("you are now logged in as {}").format(login_session['username']))
    return output


@app.route("/gdisconnect")
def gdisconnect():
    """Tries to log out a user from their Google account
    Raises any appropriate errors if there were any during
    the exchange of information
    """
    # Check if there is a user logged in
    access_token = login_session.get("access_token")
    if access_token is None:
        return JSONDumpsResponse("Current user not connected", 401)

    # Try to make a request to revoke the token
    url = "https://accounts.google.com/o/oauth2/revoke?token={}"
    url = (url).format(access_token)
    h = httplib2.Http()
    result = h.request(url, "GET")[0]

    # if revoking was successful, delete the user data
    if result["status"] == '200':
        del login_session["access_token"]
        del login_session["gplus_id"]
        del login_session["username"]
        del login_session["email"]
        del login_session["picture"]
        del login_session["user_id"]
        flash("You have been successfully logged out.")
        return redirect("/")
    else:
        return JSONDumpsResponse("Failed to revoke token for given user", 400)


@app.route("/")
@app.route("/catalog")
def showCatalog():
    """Grabs all of the categories in the database and
    outputs them to the user
    """
    categories = getAllCategories()
    return render_template("catalog.html", categories=categories)


@app.route("/catalog/<string:category_name>/items")
def showCategoryItems(category_name):
    """Grabs all of the items in the database for a
    given category and outputs them to the user

    Args:
            category_name (str): The category to grab items from
    """
    categories = getAllCategories()
    category = getCategory(category_name)
    if category is None:
        return ("Category {} not found").format(category_name)
    itemsForWeb = getAllItemsInCategory(category)
    return render_template("category.html", categories=categories,
                           items=itemsForWeb, category=category)


@app.route("/catalog/<string:category_name>/<string:item_title>")
def showItem(category_name, item_title):
    """Grabs the item from the database within the
    given category with the specified title and
    outputs it to the user

    Args:
            category_name (str): The category to grab the item from
            item_title (str): The title of the item to search for
    """
    category = getCategory(category_name)
    if category is None:
        return ("Category {} not found").format(category_name)
    item = getItem(category, item_title)
    if item is None:
        return ("Item {} not found").format(item_title)
    creator = getUserInfo(item.user_id)
    if "user_id" in login_session and creator.id == login_session["user_id"]:
        return render_template("item.html", category=category,
                               item=item, creator=creator)
    else:
        return render_template("publicitem.html", category=category,
                               item=item, creator=creator)

@app.route("/catalog/add", methods=["GET", "POST"])
@login_required
def addItem():
    """Tries to add a new item to the database
    """
    categories = getAllCategories()
    if request.method == "POST":
        # Check to make sure the item is given a title
        if not request.form['title']:
            flash("Item needs a title!")
            return render_template("addItem.html", categories=categories)
        # Check to make sure the title is unique for that category
        if not isUniqueTitle(request.form["cat_id"], request.form["title"]):
            flash("That item already exists in this category!")
            return (render_template("addItem.html", categories=categories))
        # Create the item and commit it
        item = Item(title=request.form["title"],
                    description=request.form["description"],
                    cat_id=request.form["cat_id"],
                    user_id=login_session["user_id"])
        session.add(item)
        session.commit()
        flash("Item sucessfully created!")
        return redirect("/catalog")
    return render_template("addItem.html", categories=categories)

@app.route("/catalog/<string:category_name>/<string:item_title>/edit",
           methods=["GET", "POST"])
@login_required
def editItem(category_name, item_title):
    """Tries to edit an item in the database

    Args:
            category_name: The original category of the item being edited
            item_title: The original title of the item being edited
    """
    # Initial checks to see if the user is allowed to edit
    categories = getAllCategories()
    category = getCategory(category_name)
    if category is None:
        return ("Category {} not found").format(category_name)
    item = getItem(category, item_title)
    if item is None:
        return ("Item {} not found").format(item_title)
    if item.user_id != login_session["user_id"]:
        return ("<script>function myFunction() "
                "{alert('You are not authorized to edit this item. "
                "Please create your own item in order to edit.');}"
                "</script><body onload='myFunction()'>")

    if request.method == "POST":
        editedItem = item
        category = session.query(Category).filter_by(
            id=request.form["cat_id"]).one()
        # Check to make sure the new title given is unique in its category
        if request.form["title"]:
            if not isUniqueTitle(request.form["cat_id"],
                                 request.form["title"]):
                flash("That item already exists in this category!")
                return redirect(url_for("editItem",
                                        category_name=category_name,
                                        item_title=item_title))
            else:
                editedItem.title = request.form["title"]
        if request.form["description"]:
            editedItem.description = request.form["description"]
        # Make sure title is still unique in the newly assigned category
        if not request.form["cat_id"] == str(item.cat_id):
            if request.form["title"]:
                currentTitle = request.form["title"]
            else:
                currentTitle = editedItem.title
            if not isUniqueTitle(request.form["cat_id"], currentTitle):
                flash("That item already exists in this category!")
                return redirect(url_for("editItem",
                                        category_name=category_name,
                                        item_title=item_title))
            else:
                editedItem.cat_id = request.form["cat_id"]
        session.add(editedItem)
        session.commit()
        flash("Item sucessfully edited!")
        return redirect(url_for("showItem",
                                category_name=category.name,
                                item_title=editedItem.title))
    return render_template("editItem.html",
                           categories=categories,
                           item=item,
                           category=category)

@app.route("/catalog/<string:category_name>/<string:item_title>/delete",
           methods=["GET", "POST"])
@login_required
def deleteItem(category_name, item_title):
    """Tries to delete an item from the database

    Args:
            category_name (str): The category of the item being deleted
            item_title (str): The original title of the item being edited
    """
    # Initial checks to see if the user is allowed to delete
    category = getCategory(category_name)
    if category is None:
        return ("Category {} not found").format(category_name)
    item = getItem(category, item_title)
    if item is None:
        return ("Item {} not found").format(item_title)
    if item.user_id != login_session["user_id"]:
        return ("<script>function myFunction() "
                "{alert('You are not authorized to delete this item. "
                "Please create your own item in order to delete."
                "');}</script><body onload='myFunction()'>")

    if request.method == "POST":
        session.delete(item)
        session.commit()
        flash(("Successfully deleted {}").format(item.title))
        return redirect(url_for('showCategoryItems',
                                category_name=category.name))
    return render_template("deleteItem.html", item=item, category=category)


if __name__ == "__main__":
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host="0.0.0.0", port=8000)
