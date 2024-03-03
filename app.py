from flask import Flask

import pymongo
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

