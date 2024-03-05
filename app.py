import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymongo
from bson.objectid import ObjectId
import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "namelessSecretKey"
app.config['UPLOAD_FOLDER'] = 'uploads'  # project relative path

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
'''
MongoDB Connection
'''
databaseConnection = pymongo.MongoClient("mongodb+srv://nameless:nameless@snapcook.ialrfj9.mongodb.net/?retryWrites=true&w=majority&appName=SnapCook")
database = databaseConnection["SnapCook"]
#databaseConnection = pymongo.MongoClient(os.getenv("MONGO_URI"))
#database = databaseConnection[os.getenv("MONGO_DBNAME")]
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
        search_results = recipes.find({"searchField": search_term})
    items = recipes.find()
    return render_template('home.html', items=items, search_results=search_results)

@app.route('/Fridge', methods=['GET'])
def myFridge():
    items = fridge.find()
    return render_template('myFridge.html', items=items)

@app.route('/Camera', methods=['GET', 'POST'])
def cameraScanner():
    if request.method == 'POST':
        if 'cameraInput' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['cameraInput']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        name = request.form.get('name')
        dateAcquired = datetime.datetime.now()
        estimatedExpiration = datetime.datetime.strptime(request.form.get('expiration'),'%Y-%m-%d')
        quantity = request.form.get('quantity')
        unit = request.form.get('unit')
        if name and dateAcquired and estimatedExpiration and quantity and unit:
            fridge.insert_one({'name':name, 'dateAcquired':dateAcquired, 'estimatedExpiration':estimatedExpiration, 'quantity':quantity, 'unit':unit})
        else:
            return redirect(url_for('manualEntry'))
    return render_template('cameraScanner.html')




'''
@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as {session["username"]}'
    return redirect(url_for('login'))
    
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

IDEALLY SOMEWHERE NEAR EACH INGREDIENT IN THE MY FRIDGE PAGE
@app.route('/deleteIng', methods=['POST'])
def deleteIngredient():
    itemName = request.form.get('name')
    if itemName:
        fridge.delete_one({'name': itemName})
        return redirect(url_for('myFridge'))
    return 'item name not provided', 400

GOES IN CAMERA SCANNER PAGE
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

THIS IS THE PAGE THAT SHOWS AFTER YOU CLICK INTO A RECIPE
@app.route('/recipePage', methods=['GET'])
def recipePage():
    recipeItems = recipes.find()
    ingredients = fridge.find()
    return render_template('recipePage.html', recipeItems=recipeItems, ingredients=ingredients)

BUY MISSING INGREDIENTS
@app.route('/missingIngredients')
def missingIngredients():
    return render_template('missingIngredients.html')


*/
'''
