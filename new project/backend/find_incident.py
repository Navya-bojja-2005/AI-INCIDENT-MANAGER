from pymongo import MongoClient
import os
from bson.objectid import ObjectId

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "incident_db"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
incidents_collection = db["incidents"]

def find_incident():
    print("--- ALL INCIDENTS ---")
    incidents = list(incidents_collection.find())
    if not incidents:
        print("No incidents found in database.")
        return
        
    for inc in incidents:
        print(f"ID: {inc['_id']}")
        print(f"  Number: {inc.get('incident_number')}")
        print(f"  Description: {inc.get('description')}")
        print(f"  Status: {inc.get('status')}")
        print(f"  Company: {inc.get('company')}")
        print("-" * 20)

if __name__ == "__main__":
    find_incident()
