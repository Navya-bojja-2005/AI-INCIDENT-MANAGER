
from database import users_collection, incidents_collection
from ai_engine import assign_engineer_rule_based

print("--- 1. CHECKING SUPPORT USERS ---")
support_users = users_collection.find({"role": "support"})
for u in support_users:
    print(f"User: {u.get('email')} | Dept: {u.get('department')} | Role: {u.get('role')}")

print("\n--- 2. CHECKING INCIDENTS & RE-CLASSIFYING ---")
open_incidents = incidents_collection.find({"status": "Open"})
for inc in open_incidents:
    num = inc.get('incident_number')
    desc = inc.get('description', '')
    curr_group = inc.get('assigned_group', 'Unassigned')
    
    # Run new logic
    new_group = assign_engineer_rule_based(desc)
    
    print(f"[{num}] Group: {curr_group} -> New Prediction: {new_group}")
    print(f"    Desc: {desc[:50]}...")
    
    # Optional: Fix it if it mismatches?
    if new_group != curr_group and new_group != "General Support":
        print(f"    -> UPDATING {num} to {new_group}")
        incidents_collection.update_one(
            {"incident_number": num},
            {"$set": {"assigned_group": new_group}}
        )
