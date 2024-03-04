import os
from flask import Flask, render_template, request, redirect, url_for, session
import pymongo
from bson.objectid import ObjectId
import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

databaseConnection = pymongo.MongoClient("mongodb+srv://nameless:nameless@snapcook.ialrfj9.mongodb.net/?retryWrites=true&w=majority&appName=SnapCook")
database = databaseConnection["SnapCook"]
fridge = database["Fridge"]
recipes = database["Recipes"]
users = database["Users"]

# the following try/except block is a way to verify that the database connection is alive (or not)
try:
    # verify the connection works by pinging the database
    databaseConnection.admin.command("ping")  # The ping command is cheap and does not require auth.
    print(" *", "Connected to MongoDB!")  # if we get here, the connection worked!
except Exception as e:
    # the ping command failed, so the connection is not available.
    print(" * MongoDB connection error:", e)  # debug


@app.route('/')
def index():
    if 'username' in session:
        return f'Logged in as {session["username"]}'
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({'username': username, 'password':password})

        if user:
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/signUp', methods=['POST'])
def signUp():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = users.find_one({'username': username})
        if existing_user is None:
            users.insert_one({'username': username, 'password': password})
            return redirect(url_for('login'))
        else:
            return 'Username already exists'
    return render_template('signUp.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    search_results = None
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        search_results = recipes.find({"searchField": search_term})
    items = recipes.find()
    return render_template('home.html', items=items, search_results=search_results)

@app.route('/myFridge', method=['GET'])
def myFridge():
    items = fridge.find()
    return render_template('myFridge.html', items=items)

@app.route('/deleteIng', methods=['POST'])
def deleteIngredient():
    itemName = request.form.get('name')
    if itemName:
        fridge.delete_one({'name': itemName})
        return redirect(url_for('myFridge'))
    return 'item name not provided', 400

@app.route('/cameraScanner', methods=['POST'])
def cameraScanner():
    name = request.form.get('name')
    dateAcquired = datetime.datetime.now()
    estimatedExpiration = datetime.strptime(request.form.get('expiration'),'%Y-%m-%d')
    quantity = request.form.get('quantity')
    unit = request.form.get('unit')
    if name and dateAcquired and estimatedExpiration and quantity and unit:
        fridge.insert_one({'name':name, 'dateAcquired':dateAcquired, 'estimatedExpiration':estimatedExpiration, 'quantity':quantity, 'unit':unit})
    else:
        redirect(url_for('manualEntry'))
    return render_template('cameraScanner.html')

@app.route('/manualEntry', methods=['POST'])
def manualEntry():
    name = request.form('name')
    dateAcquired = datetime.datetime.now()
    estimatedExpiration = datetime.strptime(request.form('expiration'),'%Y-%m-%d')
    quantity = request.form('quantity')
    unit = request.form('unit')
    if name and dateAcquired and estimatedExpiration and quantity and unit:
        fridge.insert_one({'name':name, 'dateAcquired':dateAcquired, 'estimatedExpiration':estimatedExpiration, 'quantity':quantity, 'unit':unit})
    else:
        return 'Missing arguments'
    return render_template('manualEntry.html')

@app.route('/recipePage', methods=['GET'])
def recipePage():
    recipeItems = recipes.find()
    ingredients = fridge.find()
    return render_template('recipePage.html', recipeItems=recipeItems, ingredients=ingredients)

@app.route('/missingIngredients')
def missingIngredients():
    return render_template('missingIngredients.html')

if __name__ == '__main__':
    app.run(debug=True)