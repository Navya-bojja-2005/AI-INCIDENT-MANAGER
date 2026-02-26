
from database import users_collection

print("--- CHECKING SUPPORT DEPARTMENTS ---")
users = users_collection.find({"role": "support"})
for u in users:
    email = u.get("email")
    dept = u.get("department")
    print(f"User: {email} | Dept: '{dept}'")
    
    # Auto-fix known mismatches
    if dept == "Application Support Engineer":
        print(f"  -> FIXING {email} to 'Application Support Team'")
        users_collection.update_one({"email": email}, {"$set": {"department": "Application Support Team"}})
    elif dept == "Network Engineer":
        print(f"  -> FIXING {email} to 'Network Support Team'")
        users_collection.update_one({"email": email}, {"$set": {"department": "Network Support Team"}})
    elif dept == "Infrastructure Engineer":
        print(f"  -> FIXING {email} to 'Infrastructure Team'")
        users_collection.update_one({"email": email}, {"$set": {"department": "Infrastructure Team"}})
    # Add more as needed based on old vs new names
