import os
from pymongo import MongoClient
from dotenv import load_dotenv
import logging
from bson import ObjectId
from bson.json_util import dumps

# Load environment variables
load_dotenv()

# Environment variable setup
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))  # Default port is 27017

def mongo_connect():
    try:
        client = MongoClient(
            f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}"
        )
        return client.db  # Return the specific database
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        raise

def mongo_device_list():
    db = mongo_connect()
    try:
        command = list(
            db.voices.aggregate([
                {"$group": {
                    "_id": "$device_id",
                    "latest_entry": {"$last": "$$ROOT"}
                }},
                {"$replaceRoot": {"newRoot": "$latest_entry"}}
            ])
        )
        return dumps(command)
    except Exception as e:
        logging.error(f"Error fetching unique device_id: {e}")
        return None

def mongo_user_list():
    db = mongo_connect()
    try:
        command = list(
            db.users.aggregate([
                {"$group": {
                    "_id": "$user_id",
                    "latest_entry": {"$last": "$$ROOT"}
                }},
                {"$replaceRoot": {"newRoot": "$latest_entry"}}
            ])
        )
        return dumps(command)
    except Exception as e:
        logging.error(f"Error fetching unique user_id: {e}")
        return None

def mongo_user_insert(user_data):
    db = mongo_connect() 
    try:
        db.users.insert_one(user_data)
        logging.info("User data inserted successfully")
    except Exception as e:
        logging.error(f"Error inserting user data: {e}")
