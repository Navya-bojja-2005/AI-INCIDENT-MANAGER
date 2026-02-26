from pymongo import MongoClient
import os
import json
from bson.objectid import ObjectId
from datetime import datetime

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "incident_db"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
incidents_collection = db["incidents"]

def dump_all_incidents():
    incidents = list(incidents_collection.find())
    with open("all_incidents.json", "w") as f:
        json.dump(incidents, f, cls=JSONEncoder, indent=2)
    print(f"Dumped {len(incidents)} incidents to all_incidents.json")

if __name__ == "__main__":
    dump_all_incidents()
