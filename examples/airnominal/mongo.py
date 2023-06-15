from pymongo import MongoClient

from config import mongo_url, port, username, password

client = MongoClient(mongo_url, port, username=username, password=password)

db = client.airnominal
stations = db.stations
tokens = db.tokens
sensors = db.sensors
units = db.units
measuerments = db.measuerments
