
from database import users_collection

print("--- FIXING NETWORK USER DEPARTMENT ---")
user_email = "pavi@tcs.com"
new_dept = "Network Support Team"

result = users_collection.update_one(
    {"email": user_email},
    {"$set": {"department": new_dept}}
)

if result.modified_count > 0:
    print(f"SUCCESS: Updated {user_email} to '{new_dept}'")
else:
    user = users_collection.find_one({"email": user_email})
    if user:
        print(f"NO CHANGE: User {user_email} already has dept '{user.get('department')}'")
    else:
        print(f"ERROR: User {user_email} not found!")
