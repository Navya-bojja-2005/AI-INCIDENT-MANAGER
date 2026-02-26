from pymongo import MongoClient
import os
from bson.objectid import ObjectId

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "incident_db"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
incidents_collection = db["incidents"]

def delete_incident(target_id):
    print(f"Attempting to delete incident with ID: {target_id}...")
    result = incidents_collection.delete_one({"_id": ObjectId(target_id)})
    if result.deleted_count > 0:
        print("Successfully deleted the incident.")
    else:
        print("No incident found with that ID.")

if __name__ == "__main__":
    # Target ID identified from dump: 69956051384bd3af29c5388f
    delete_incident("69956051384bd3af29c5388f")
