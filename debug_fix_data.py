
from database import users_collection, incidents_collection, get_user

print("--- FIXING REF DATA ---")

# 1. Update User
print("Updating user pavi@tcs.com...")
res_u = users_collection.update_one(
    {'email': 'pavi@tcs.com'}, 
    {'$set': {
        'department': 'Network Team', 
        'company': 'tcs.com',
        'role': 'support' # Ensure lowercase
    }}
)
print(f"User Update Acknowledged: {res_u.acknowledged}, Modified: {res_u.modified_count}")

# 2. Update Incident
print("Updating INC-1014...")
res_i = incidents_collection.update_one(
    {'incident_number': 'INC-1014'}, 
    {'$set': {
        'assigned_to': None, 
        'status': 'Open', 
        'assigned_group': 'General Support'
    }}
)
print(f"Incident Update Acknowledged: {res_i.acknowledged}, Modified: {res_i.modified_count}")

# 3. Verify
u = get_user('pavi@tcs.com')
print(f"VERIFY USER -> Email: {u.get('email')} | Dept: {u.get('department')} | Role: {u.get('role')}")

inc = incidents_collection.find_one({'incident_number': 'INC-1014'})
print(f"VERIFY INC -> ID: {inc.get('incident_number')} | Group: {inc.get('assigned_group')} | Assignee: {inc.get('assigned_to')}")
