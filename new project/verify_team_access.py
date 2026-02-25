
import os
import sys
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import init_db, create_user, users_collection, incidents_collection, create_incident, get_incidents_by_role

def test_team_access():
    print("--- Testing Team-Based Access ---")
    
    # 1. Setup Data
    print("Setting up test data...")
    users_collection.delete_many({"email": {"$regex": "test_.*@tcs.com"}})
    incidents_collection.delete_many({"created_by": "test_emp@tcs.com"})
    
    # Create Users
    create_user("test_net@tcs.com", "pass", "support", "Network Engineer")
    create_user("test_infra@tcs.com", "pass", "support", "Infrastructure Engineer")
    create_user("test_emp@tcs.com", "pass", "employee")
    
    # Create Incidents
    id1 = create_incident("Wifi down", "High", "test_emp@tcs.com", "Dev", "Network Engineer")
    id2 = create_incident("Server crash", "High", "test_emp@tcs.com", "Dev", "Infrastructure Engineer")
    id3 = create_incident("App error", "Medium", "test_emp@tcs.com", "Dev", "Application Support Engineer")
    
    print("Incidents created.")
    
    # 2. Verify Network Engineer View
    print("\n[Network Engineer View]")
    net_incidents = get_incidents_by_role("support", "test_net@tcs.com")
    
    # Should see "Wifi down"
    wifi_found = any(i['description'] == "Wifi down" for i in net_incidents)
    # Should NOT see "Server crash"
    server_found = any(i['description'] == "Server crash" for i in net_incidents)
    
    print(f"Sees Wifi Issue: {wifi_found} (Expected True)")
    print(f"Sees Server Issue: {server_found} (Expected False)")
    
    if wifi_found and not server_found:
        print(">>> NETWORK VIEW PASS")
    else:
        print(">>> NETWORK VIEW FAIL")

    # 3. Verify Infrastructure Engineer View
    print("\n[Infrastructure Engineer View]")
    infra_incidents = get_incidents_by_role("support", "test_infra@tcs.com")
    
    # Should see "Server crash"
    server_found_infra = any(i['description'] == "Server crash" for i in infra_incidents)
    # Should NOT see "Wifi down"
    wifi_found_infra = any(i['description'] == "Wifi down" for i in infra_incidents)
    
    print(f"Sees Server Issue: {server_found_infra} (Expected True)")
    print(f"Sees Wifi Issue: {wifi_found_infra} (Expected False)")
    
    if server_found_infra and not wifi_found_infra:
        print(">>> INFRA VIEW PASS")
    else:
        print(">>> INFRA VIEW FAIL")
        
    # Cleanup
    print("\nCleaning up...")
    users_collection.delete_many({"email": {"$regex": "test_.*@tcs.com"}})
    incidents_collection.delete_many({"created_by": "test_emp@tcs.com"})
    print("Done.")

if __name__ == "__main__":
    init_db()
    test_team_access()
