
from app import app
from database import users_collection

print("--- VERIFYING REGISTRATION LOGIC ---")

# Setup
client = app.test_client()
email_emp = "test_employee_nodept@tcs.com"
email_sup = "test_support_nodept@tcs.com"

# Cleanup
users_collection.delete_many({"email": {"$in": [email_emp, email_sup]}})

# 1. Test Employee Registration (Should Succeed without Dept)
print(f"Testing Employee Registration ({email_emp})...")
response_emp = client.post('/register', data={
    "email": email_emp,
    "password": "password123",
    "role": "employee"
    # No department
}, follow_redirects=True)

# Check if user created
user_emp = users_collection.find_one({"email": email_emp})
if user_emp:
    print("SUCCESS: Employee user created without department.")
else:
    print("FAILURE: Employee user NOT created.")
    print(response_emp.data.decode())

# 2. Test Support Registration (Should Fail without Dept)
print(f"Testing Support Registration ({email_sup})...")
response_sup = client.post('/register', data={
    "email": email_sup,
    "password": "password123",
    "role": "support"
    # No department
}, follow_redirects=True)

# Check if user created
user_sup = users_collection.find_one({"email": email_sup})
if not user_sup:
    # Check for error message
    if "Department is required" in response_sup.data.decode():
        print("SUCCESS: Support user rejected (Department required).")
    else:
        print("WARNING: Support user rejected but error message mismatch.")
else:
    print("FAILURE: Support user created without department!")

# Cleanup
users_collection.delete_many({"email": {"$in": [email_emp, email_sup]}})
