
from database import users_collection, incidents_collection, get_incidents_by_role

print("--- 1. CHECKING NETWORK SUPPORT USERS ---")
support_users = users_collection.find({"role": "support"})
for u in support_users:
    print(f"User: {u.get('email')} | Dept: '{u.get('department')}'")

print("\n--- 2. CHECKING RECENT INCIDENTS ---")
recent_incidents = incidents_collection.find().sort("created_at", -1).limit(5)
for inc in recent_incidents:
    print(f"ID: {inc.get('incident_number')} | Desc: {inc.get('description')[:50]}... | Group: '{inc.get('assigned_group')}' | Status: '{inc.get('status')}'")

print("\n--- 3. CHECKING VISIBILITY for 'pavi@tcs.com' ---")
# Assuming pavi is the network engineer
pavi_incidents = get_incidents_by_role("support", "pavi@tcs.com", "tcs.com")
print(f"Incidents visible to pavi: {len(pavi_incidents)}")
for i in pavi_incidents:
    print(f" - {i.get('incident_number')}: {i.get('assigned_group')}")
