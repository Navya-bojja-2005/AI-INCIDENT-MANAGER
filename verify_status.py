
from database import create_incident, get_incidents_by_role, incidents_collection

print("--- TESTING 'SUBMITTED' STATUS ---")

# 1. Create Incident
print("Creating test incident...")
inc_id = create_incident(
    description="Test Incident for Status Check",
    priority="Low",
    created_by="test_user@example.com",
    employee_role="Tester",
    assigned_group="Application Support Team",
    company="tcs.com"
)
print(f"Incident Created: ID {inc_id}")

# 2. Verify Status
inc = incidents_collection.find_one({"_id": inc_id})
print(f"Status: {inc.get('status')} (Expected: Open)")

# 3. Verify Visibility for Network Support (pavi@tcs.com)
# Pavi is in "Network Support Team". The incident is assigned to "Application Support Team".
# Pavi should NOT see it.
print("Checking visibility for 'pavi@tcs.com' (Network Support Team)...")
incidents = get_incidents_by_role("support", "pavi@tcs.com", "tcs.com")
found = any(str(i['_id']) == str(inc_id) for i in incidents)
print(f"Visible to Pavi? {found} (Expected: False)")

# Cleanup
incidents_collection.delete_one({"_id": inc_id})
print("Test incident deleted.")
