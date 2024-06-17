# mongodb_config.py
from pymongo import MongoClient
from datetime import datetime


def get_mongodb_connection():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['tienda_online']
    return db



