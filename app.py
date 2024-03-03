import os
from flask import Flask, render_template
import pymongo
from bson.objectid import ObjectId
import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

#databaseConnection = pymongo.MongoClient("mongodb+srv://nameless:nameless@snapcook.ialrfj9.mongodb.net/?retryWrites=true&w=majority&appName=SnapCook")
#database = databaseConnection["SnapCook"]
databaseConnection = pymongo.MongoClient(os.getenv("MONGO_URI"))
database = databaseConnection[os.getenv("MONGO_DBNAME")]

# the following try/except block is a way to verify that the database connection is alive (or not)
try:
    # verify the connection works by pinging the database
    databaseConnection.admin.command("ping")  # The ping command is cheap and does not require auth.
    print(" *", "Connected to MongoDB!")  # if we get here, the connection worked!
except Exception as e:
    # the ping command failed, so the connection is not available.
    print(" * MongoDB connection error:", e)  # debug

@app.route('/')
def homePage():
    return render_template("index.html")