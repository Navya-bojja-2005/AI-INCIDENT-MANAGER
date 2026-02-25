from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

# Database Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "incident_db"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
users_collection = db["users"]
incidents_collection = db["incidents"]

def init_db():
    """Check connection and create indexes if needed"""
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        # Create index on email (the new unique identifier)
        # We also attempt to drop the old 'username' index if it exists to clean up
        indexes = users_collection.index_information()
        if "username_1" in indexes:
             users_collection.drop_index("username_1")
             print("Dropped legacy 'username' index on startup.")
             
        users_collection.create_index("email", unique=True)
        print("Ensured 'email' unique index.")
    except Exception as e:
        print(f"MongoDB Connection/Index Error: {e}")

# --- User Operations ---
def create_user(email, password, role, department=None):
    if users_collection.find_one({"email": email}):
        return False
    
    # Extract company from email (domain)
    # e.g. alice@wipro.com -> wipro.com
    company = email.split('@')[-1]

    users_collection.insert_one({
        "email": email,
        "password": password, # In production, hash this!
        "role": role, # 'employee', 'support', 'admin'
        "department": department, # 'Infrastructure Engineer', 'Network Engineer', etc.
        "company": company,
        "created_at": datetime.utcnow()
    })
    return True

def get_user(email):
    return users_collection.find_one({"email": email})

# --- Incident Operations ---
# --- Sequence Helper ---
def get_next_sequence(sequence_name):
    # Atomic increment
    # Initialize connection if not exists (lazy loaded usually, but db global here)
    counter = db.counters.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]

# --- Incident Operations ---
def create_incident(description, priority, created_by, employee_role="Unspecified", assigned_group="Support", company=None):
    # Generate readable ID
    # Start from 1000 if not set, handled by upsert but we might want to seed it if 0.
    # actually upsert sets it to 1 if not exists? No, $inc treats missing as 0 then adds 1.
    # So first one will be 1. We want INC-1001? 
    # Let's just use simple increment. If user wants 1000 start, we can seed it or just add 1000.
    # Let's add 1000 to the sequence.
    
    seq_num = get_next_sequence("incident_id")
    incident_number = f"INC-{seq_num + 1000}" 

    incident_id = incidents_collection.insert_one({
        "incident_number": incident_number,
        "description": description,
        "priority": priority, # 'High', 'Medium', 'Low'
        "status": "Open", # 'Open', 'In Progress', 'Resolved', 'Closed'
        "created_by": created_by,
        "employee_role": employee_role,
        "assigned_group": assigned_group, # Auto-assigned group (e.g., Infrastructure Engineer)
        "assigned_to": None, # Specific individual user (initially None)
        "company": company,
        "created_at": datetime.utcnow(),
        "major_incident_group": None # ID of the major incident if grouped
    }).inserted_id
    return incident_id

def get_all_incidents(company=None):
    query = {}
    if company:
        query["company"] = company
    return list(incidents_collection.find(query).sort("created_at", -1))

def get_incidents_by_role(role, username=None, company=None):
    query = {}
    if company:
        query["company"] = company

    if role == "employee":
        query["created_by"] = username
        return list(incidents_collection.find(query).sort("created_at", -1))
    elif role == "support":
        # Support sees ONLY:
        # 1. Incidents assigned to them (In Progress/Resolved)
        # 2. Open incidents assigned to their TEAM (Department)
        
        user = get_user(username)
        department = user.get('department')
        
        # Base condition: Always see assigned to me
        or_conditions = [
            {"assigned_to": username}
        ]

        if department:
             # See Open incidents for MY Department
             or_conditions.append({
                "$and": [
                    {"status": "Open"},
                    {"assigned_group": department}
                ]
             })
        
        # Combine with company filter
        final_query = {
            "$and": [
                {"company": company},
                {"$or": or_conditions}
            ]
        }
        
        return list(incidents_collection.find(final_query).sort("priority_rank", 1))
        
    # Default fallback (should satisfy company filter)
    return list(incidents_collection.find(query).sort("created_at", -1))

def get_incidents_filtered(filter_type, company=None):
    """
    Get incidents based on a specific filter for Admin view.
    """
    query = {}
    if company:
        query['company'] = company

    if filter_type == 'total':
        pass # No filter
    elif filter_type == 'high':
        query['priority'] = 'High'
    elif filter_type == 'medium':
        query['priority'] = 'Medium'
    elif filter_type == 'low':
        query['priority'] = 'Low'
    elif filter_type == 'open':
        query['status'] = 'Open'
    elif filter_type == 'escalated':
        query['escalated'] = True
    elif filter_type == 'major':
        query['major_incident_group'] = {"$ne": None}

        
    return list(incidents_collection.find(query).sort("created_at", -1))

def get_incidents_by_status(username, status_list):
    """
    Get incidents for a specific user filtered by a list of statuses.
    """
    return list(incidents_collection.find({
        "created_by": username,
        "status": {"$in": status_list}
    }).sort("created_at", -1))

def update_incident_status(incident_id, status, assigned_to=None, action_taken=None, resolved_at=None):
    update_data = {"status": status}
    
    if assigned_to:
        update_data["assigned_to"] = assigned_to
        
    if action_taken:
        update_data["action_taken"] = action_taken
        
    if resolved_at:
        update_data["resolved_at"] = resolved_at
        
    # If starting progress, set SLA start time
    if status == "In Progress":
        update_data["sla_start_time"] = datetime.utcnow()

    incidents_collection.update_one(
        {"_id": ObjectId(incident_id)},
        {"$set": update_data}
    )

def flag_major_incident(incident_ids, group_name):
    # Group multiple incidents under a major incident tag
    for i_id in incident_ids:
        incidents_collection.update_one(
            {"_id": ObjectId(i_id)},
            {"$set": {"major_incident_group": group_name, "priority": "High"}}
        )

def get_open_incidents_validation(company=None):
    """Helper for AI similarity check"""
    query = {"status": {"$in": ["Open", "In Progress"]}}
    if company:
        query["company"] = company
    return list(incidents_collection.find(query))

def check_and_escalate_incidents():
    """
    Check for incidents that have been 'In Progress' for too long and escalate them.
    Escalation rules:
    - High: > 1 hour
    - Medium: > 2 hours
    - Low: > 3 hours
    """
    import datetime
    now = datetime.datetime.utcnow()
    
    # Define thresholds
    threshold_high = now - datetime.timedelta(hours=1)
    threshold_medium = now - datetime.timedelta(hours=2)
    threshold_low = now - datetime.timedelta(hours=3)
    
    count = 0
    
    # escalate High
    res_high = incidents_collection.update_many(
        {
            "status": "In Progress",
            "escalated": {"$ne": True},
            "priority": "High",
            "sla_start_time": {"$lt": threshold_high} # User sla_start_time if available, else fallback to created_at logic if needed (but we add sla_start_time now)
        },
        {"$set": {"escalated": True}}
    )
    count += res_high.modified_count
    
    # escalate Medium
    res_med = incidents_collection.update_many(
        {
            "status": "In Progress",
            "escalated": {"$ne": True},
            "priority": "Medium",
            "sla_start_time": {"$lt": threshold_medium}
        },
        {"$set": {"escalated": True, "priority": "High"}} # Bump to High
    )
    count += res_med.modified_count

    # escalate Low
    res_low = incidents_collection.update_many(
        {
            "status": "In Progress",
            "escalated": {"$ne": True},
            "priority": "Low",
            "sla_start_time": {"$lt": threshold_low}
        },
        {"$set": {"escalated": True, "priority": "High"}} # Bump to High
    )
    count += res_low.modified_count
    

def rate_incident(incident_id, rating):
    """
    Update incident with a satisfaction rating (1-5).
    """
    incidents_collection.update_one(
        {"_id": ObjectId(incident_id)},
        {"$set": {"rating": int(rating)}}
    )

def get_engineer_stats(company=None):
    """
    Aggregate stats for support engineers:
    - Average Rating
    - Average Resolution Time (in hours)
    - Total Resolved
    """
    match_stage = {"status": "Resolved", "assigned_to": {"$ne": None}, "resolved_at": {"$ne": None}}
    if company:
        match_stage["company"] = company

    pipeline = [
        # Filter for resolved incidents that have an assignee
        {"$match": match_stage},
        
        # Calculate resolution duration in milliseconds (resolved_at - created_at)
        # Note: In a real app, we might use sla_start_time if available
        {"$addFields": {
            "duration_ms": {"$subtract": ["$resolved_at", "$created_at"]}
        }},
        
        # Group by Assigned Engineer
        {"$group": {
            "_id": "$assigned_to",
            "total_resolved": {"$sum": 1},
            "avg_rating": {"$avg": "$rating"}, # Will ignore null ratings automatically
            "avg_duration": {"$avg": "$duration_ms"}
        }},
        
        # Sort by best rating
        {"$sort": {"avg_rating": -1}}
    ]
    
    results = list(incidents_collection.aggregate(pipeline))
    
    # Format output
    stats = []
    for r in results:
        # Convert duration to hours
        hours = round(r['avg_duration'] / (1000 * 60 * 60), 2) if r['avg_duration'] else 0
        
        stats.append({
            "email": r['_id'],
            "total": r['total_resolved'],
            "avg_rating": round(r['avg_rating'], 1) if r['avg_rating'] else "N/A",
            "avg_time_hours": hours
        })
        
    return stats
