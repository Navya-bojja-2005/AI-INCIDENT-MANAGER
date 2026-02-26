from pymongo import MongoClient
import os
import json
from bson.objectid import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "incident_db"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
incidents_collection = db["incidents"]

def find_specific_incident():
    # Search for "wifi" in description
    query = {"description": {"$regex": "wifi", "$options": "i"}}
    incidents = list(incidents_collection.find(query))
    
    with open("found_incidents.json", "w") as f:
        json.dump(incidents, f, cls=JSONEncoder, indent=2)
    
    print(f"Found {len(incidents)} incidents. Details saved to found_incidents.json")

if __name__ == "__main__":
    find_specific_incident()
