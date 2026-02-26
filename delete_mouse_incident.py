
from database import incidents_collection

print("--- DELETING 'MOUSE' INCIDENT ---")

# Find the incident
query = {"description": {"$regex": "mouse", "$options": "i"}}
incidents = list(incidents_collection.find(query).sort("created_at", -1))

if not incidents:
    print("No incidents found containing 'mouse'.")
else:
    # Get the most recent one
    target_start = incidents[0]
    print(f"Found {len(incidents)} incidents.")
    print(f"Targeting most recent: {target_start['incident_number']} - '{target_start['description']}'")
    
    # Delete it
    result = incidents_collection.delete_one({"_id": target_start["_id"]})
    if result.deleted_count > 0:
        print(f"SUCCESS: Deleted incident {target_start['incident_number']}")
    else:
        print("ERROR: Could not delete incident.")
