
from database import get_user, get_all_incidents, get_incidents_by_role
from pymongo import MongoClient

# Setup connection (assuming standard localhost for debugging if modules allows, 
# otherwise relying on database.py's internal connection if it's singleton)
# Better to use database.py functions directly.

# Mocking session values for testing
email = "pavi@tcs.com" 
company = "TCS" # Assumption based on email

print(f"--- Checking User: {email} ---")
user = get_user(email)
if user:
    print(f"User Found: {user.get('username')}")
    print(f"Role: {user.get('role')}")
    print(f"Department: '{user.get('department')}'") 
    print(f"Company: {user.get('company')}")
else:
    print("User not found.")

print("\n--- Checking Incidents for Default View (My Team) ---")
# view_all = False
incidents = get_incidents_by_role('support', email, company, view_all=False)
print(f"Found {len(incidents)} incidents.")
for inc in incidents:
    print(f"ID: {inc.get('incident_number')} | Status: {inc.get('status')} | Assigned Group: '{inc.get('assigned_group')}' | Assigned To: '{inc.get('assigned_to')}'")

print("\n--- Checking Incidents for All Open View ---")
# view_all = True
incidents_all = get_incidents_by_role('support', email, company, view_all=True)
print(f"Found {len(incidents_all)} incidents.")
