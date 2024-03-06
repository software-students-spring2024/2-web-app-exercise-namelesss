import os
from flask import Flask, render_template, request, redirect, url_for, session
import pymongo
from bson.objectid import ObjectId
import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "namelessSecretKey"

'''
MongoDB Connection
'''
databaseConnection = pymongo.MongoClient(
    "mongodb+srv://nameless:nameless@snapcook.ialrfj9.mongodb.net/?retryWrites=true&w=majority&appName=SnapCook")
database = databaseConnection["SnapCook"]
# databaseConnection = pymongo.MongoClient(os.getenv("MONGO_URI"))
# database = databaseConnection[os.getenv("MONGO_DBNAME")]
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


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({'username': username, 'password': password})

        if user:
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            return redirect(url_for('invalidLogin'))
    return render_template('login.html')


@app.route('/SignUp', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = users.find_one({'username': username})
        if existing_user is None:
            users.insert_one({'username': username, 'password': password})
            return redirect(url_for('login'))
        else:
            return redirect(url_for('invalidSignUp'))
    return render_template('signUp.html')


@app.route('/InvalidLogin')
def invalidLogin():
    return render_template('invalidLogin.html')


@app.route('/InvalidSignUp')
def invalidSignUp():
    return render_template('invalidSignUp.html')


@app.route('/Home', methods=['GET', 'POST'])
def home():
    search_results = None
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        search_results = recipes.find({"$or": [
            {"recipeName": {"$regex": search_term, "$options": "i"}},
            {"ingredients": {"$regex": search_term, "$options": "i"}}
        ]})
    items = recipes.find()
    return render_template('home.html', items=items, search_results=search_results)


@app.route('/Fridge', methods=['GET'])
def myFridge():
    items = fridge.find()
    return render_template('myFridge.html', items=items)


@app.route('/Camera', methods=['GET', 'POST'])
def cameraScanner():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            dateAcquired = datetime.datetime.now()
            estimatedExpiration = datetime.datetime.strptime(request.form.get('expiration'), '%Y-%m-%d')
            quantity = float(request.form.get('quantity'))
            unit = request.form.get('unit')
            photo = request.files.get('photo')

            if name and dateAcquired and estimatedExpiration and quantity and unit:
                fridge.insert_one({
                    'name': name,
                    'dateAcquired': dateAcquired,
                    'estimatedExpiration': estimatedExpiration,
                    'quantity': quantity,
                    'unit': unit
                })
                return redirect(url_for('myFridge'))
            else:
                return redirect(url_for('manualEntry'))
        except Exception as e:
            print("Error occurred:", str(e))
            return "An error occurred while processing the request"
    return render_template('cameraScanner.html')


@app.route('/manualEntry', methods=['GET', 'POST'])
def manualEntry():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            dateAcquired = datetime.datetime.now()
            estimatedExpiration = datetime.datetime.strptime(request.form.get('estimatedExpiration'), '%Y-%m-%d')
            quantity = float(request.form.get('quantity'))
            unit = request.form.get('unit')

            if name and estimatedExpiration and quantity and unit:
                fridge.insert_one({
                    'name': name,
                    'dateAcquired': dateAcquired,
                    'estimatedExpiration': estimatedExpiration,
                    'quantity': quantity,
                    'unit': unit
                })
                return redirect(url_for('myFridge'))
            else:
                return 'Missing arguments'
        except Exception as e:
            print("Error occurred:", str(e))
            return "An error occurred while processing the request"
    return render_template('manualEntry.html')


@app.route('/recipePage/<recipe_id>', methods=['GET'])
def recipePage(recipe_id):
    try:
        recipe = recipes.find_one({"_id": ObjectId(recipe_id)})
        return render_template('recipePage.html', recipe=recipe)
    except Exception as e:
        print("Error occurred:", str(e))
        return "An error occurred while processing the request"
    

@app.route('/itemPage', methods=['GET'])
def itemPage() :
    try:
        itemName = request.form.get('name')
        item = fridge.find_one({"name" : itemName})
        return render_template('itemPage.html', item=item)
    except Exception as e:
        print("Error occurred:", str(e))
        return "An error occurred while processing the request"


@app.route('/deleteIng', methods=['POST'])
def deleteIngredient():
    itemName = request.form.get('name')
    if itemName:
        fridge.delete_one({'name': itemName})
        return '<script>window.opener.location.reload(); window.close();</script>'
    else:
        return 'item name not provided', 400


@app.route('/itemPage', methods=['GET', 'POST'])
def itemPage():
    if request.method == 'POST':
        itemName = request.form.get('name')
        newExpiration = datetime.datetime.strptime(request.form.get('estimatedExpiration'), '%Y-%m-%d')
        newQuantity = float(request.form.get('quantity'))
        newUnit = request.form.get('unit')
        if itemName:
            fridge.update_one({'name': itemName}, {'$set': {'estimatedExpiration': newExpiration, 'quantity': newQuantity, 'unit': newUnit}})
            return redirect(url_for('myFridge'))
    else:
        itemName = request.args.get('name')
        item = fridge.find_one({"name": itemName})
        return render_template('itemPage.html', item=item)


@app.route('/missingIngredients/<recipe_id>')
def missingIngredients(recipe_id):
    recipe = recipes.find_one({"_id": ObjectId(recipe_id)})
    fridge_items = fridge.find()

    missing_ingredients = []
    for ingredient in recipe['ingredients']:
        found = False
        for item in fridge_items:
            if item['name'].lower() == ingredient.lower():
                found = True
                break
        if not found:
            missing_ingredients.append(ingredient)

    return render_template('missingIngredients.html', missing_ingredients=missing_ingredients)


@app.template_filter('datetime_format')
def datetime_format(value):
    if value is None:
        return 'N/A'
    return value.strftime('%Y-%m-%d')

if __name__ == "__main__":
    app.run(debug=True)