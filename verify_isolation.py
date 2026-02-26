from database import create_user, create_incident, get_all_incidents, users_collection, incidents_collection
import time

def run_test():
    print("Starting Isolation Test...")
    
    timestamp = int(time.time())
    email_a = f"admin_a_{timestamp}@compa.com"
    email_b = f"admin_b_{timestamp}@compb.com"
    
    # Create Users (internally extracts company)
    create_user(email_a, "password", "admin")
    create_user(email_b, "password", "admin")
    
    print(f"Created users: {email_a} (compa.com), {email_b} (compb.com)")
    
    # Create Incidents
    # Note: in app.py we pass company explicitly. here we simulate that.
    create_incident("Incident for CompA", "High", email_a, company="compa.com")
    create_incident("Incident for CompB", "High", email_b, company="compb.com")
    
    print("Created incidents for both companies.")
    
    # Test Fetching
    
    # 1. Fetch for CompA
    print("\n--- Testing Fetch for CompA ---")
    incidents_a = get_all_incidents("compa.com")
    print(f"Found {len(incidents_a)} incidents.")
    
    count_a = 0
    for i in incidents_a:
        print(f" - {i['description']} (Company: {i.get('company')})")
        if i.get('company') == 'compa.com':
            count_a += 1
        else:
            print("FAILURE: Found incident from wrong company!")
            
    # We might have collisions if multiple runs, so allow >= 1, but ALL must be compa.com
    if count_a == 0:
        print("FAILURE: No incidents found for CompA.")

    # 2. Fetch for CompB
    print("\n--- Testing Fetch for CompB ---")
    incidents_b = get_all_incidents("compb.com")
    print(f"Found {len(incidents_b)} incidents.")
    
    count_b = 0
    for i in incidents_b:
        print(f" - {i['description']} (Company: {i.get('company')})")
        if i.get('company') == 'compb.com':
            count_b += 1
        else:
             print("FAILURE: Found incident from wrong company!")

    if count_b == 0:
         print("FAILURE: No incidents found for CompB.")
         
    if count_a > 0 and count_b > 0:
        print("\nTest Pas sed: Isolation logic works.")
    else:
        print("\nTest Failed.")

if __name__ == "__main__":
    run_test()
