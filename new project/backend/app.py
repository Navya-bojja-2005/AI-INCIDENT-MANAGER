from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import create_user, get_user, create_incident, get_incidents_by_role, get_all_incidents, update_incident_status, get_open_incidents_validation, init_db, get_incidents_by_status, check_and_escalate_incidents, get_incidents_filtered, get_engineer_stats
from ai_engine import analyze_incident
from datetime import timedelta
import os

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
app.permanent_session_lifetime = timedelta(days=30)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

# --- Routes ---

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = get_user(email)
        if user and user['password'] == password:
            session.permanent = True
            session['email'] = email
            session['role'] = user['role']
            # Ensure company is set (fallback to email domain if missing in DB)
            session['company'] = user.get('company') or email.split('@')[-1]
            return redirect(url_for('dashboard'))
            
        return render_template('login.html', error="Invalid credentials")
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        # Basic Server-side validation
        # Relaxed validation: Allow any email, but ensuring it has an @ and .
        if '@' not in email or '.' not in email:
             return render_template('register.html', error="Invalid email format")

        # 1. Domain Restriction Validation
        allowed_domains = [
            "tcs.com", "infosys.com", "wipro.com", "hcltech.com", 
            "accenture.com", "cognizant.com", "ibm.com", "deloitte.com", 
            "capgemini.com", "techmahindra.com"
        ]
        domain = email.split('@')[-1]
        if domain not in allowed_domains:
             return render_template('register.html', error="Registration allowed only for authorized company domains.")

        department = request.form.get('department')

        if role == 'support' and not department:
            return render_template('register.html', error="Department is required for Support roles.")

        if create_user(email, password, role, department):
             return redirect(url_for('login'))
        else:
             return render_template('register.html', error="Email already exists")
             
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
        
    email = session['email']
    
    # Fetch latest user data to ensure role/company/dept are fresh
    user = get_user(email)
    if not user:
        session.clear()
        return redirect(url_for('login'))

    # Use DB values, fallback to session if needed (though DB should have them)
    role = user.get('role', session.get('role', 'employee')).lower()
    company = user.get('company', session.get('company'))
    
    # Update session to keep it fresh (optional but good practice)
    session['role'] = role
    session['company'] = company
    
    engineer_stats = []
    
    if role == "admin":
        incidents = get_all_incidents(company)
    elif role == "support":
        incidents = get_incidents_by_role(role, email, company)
    else:
        # Employee
        incidents = get_incidents_by_role(role, email, company)
        
    return render_template('dashboard.html', incidents=incidents, role=role, email=email, user=user)

# ... (submit_incident, etc)

@app.route('/rate_incident', methods=['POST'])
def rate_incident_route():
    if 'email' not in session or session['role'] != 'employee':
         return redirect(url_for('login'))
    
    incident_id = request.form.get('incident_id')
    rating = request.form.get('rating')
    
    if incident_id and rating:
        from database import rate_incident
        rate_incident(incident_id, rating)
        
    return redirect(url_for('dashboard'))


@app.route('/submit_incident', methods=['GET', 'POST'])
def submit_incident():
    if 'email' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        description = request.form['description']
        email = session['email']
        
        # Get Employee Role from form
        employee_role = request.form.get('employee_role', 'Unspecified')

        # Run AI Analysis
        # 1. Priority (Expanded rules)
        # 2. Auto-assignment (Rule based)
        
        # Analyze incident using AI Engine
        # Pass lambda to validate against company-specific incidents
        analysis_result = analyze_incident(description, lambda: get_open_incidents_validation(session.get('company')))
        
        if 'error' in analysis_result:
             return render_template('submit_incident.html', error=analysis_result['error'])

        priority = analysis_result['priority']
        assigned_group = analysis_result['assigned_group']
        
        # If similar incident found, adjust logic or just flag it
        is_major = analysis_result.get('is_major_candidate', False)
        
        if is_major:
            # Logic to handle major incident grouping could go here
            # For simplicity, we just mark it
            priority = "High" # Force High if major incident candidate
            description += " [POTENTIAL MAJOR INCIDENT GROUPING]"
        
        create_incident(description, priority, email, employee_role, assigned_group, company=session.get('company'))
        
        return redirect(url_for('dashboard'))
        
    return render_template('submit_incident.html')

@app.route('/employee/active')
def employee_active():
    if 'email' not in session or session['role'] != 'employee':
        return redirect(url_for('login'))
        
    incidents = get_incidents_by_status(session['email'], ['Open', 'In Progress'])
    return render_template('employee_active.html', incidents=incidents)

@app.route('/employee/history')
def employee_history():
    if 'email' not in session or session['role'] != 'employee':
        return redirect(url_for('login'))
        
    incidents = get_incidents_by_status(session['email'], ['Resolved', 'Closed'])
    return render_template('employee_history.html', incidents=incidents)

@app.route('/pick_incident/<incident_id>')
def pick_incident(incident_id):
    if 'email' not in session or session['role'] != 'support':
         return redirect(url_for('login'))
         
    # Assign to current support user
    update_incident_status(incident_id, "In Progress", assigned_to=session['email'])
    return redirect(url_for('dashboard'))

@app.route('/resolve_incident', methods=['POST'])
def resolve_incident():
    if 'email' not in session or session['role'] != 'support':
         return redirect(url_for('login'))
    
    incident_id = request.form.get('incident_id')
    action_taken = request.form.get('action_taken')
    from datetime import datetime
    
    update_incident_status(incident_id, "Resolved", action_taken=action_taken, resolved_at=datetime.utcnow())
    return redirect(url_for('dashboard'))

# --- API for potential AJAX/Dynamic Updates ---
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.json
    description = data.get('description', '')
    result = analyze_incident(description, get_open_incidents_validation)
    return jsonify(result)

@app.route('/admin/trigger_escalation')
def trigger_escalation():
    if 'email' not in session or session['role'] != 'admin':
         return redirect(url_for('login'))
         
    count = check_and_escalate_incidents()
    return redirect(url_for('dashboard', msg=f"Escalation Check Run. {count} incidents escalated."))

@app.route('/admin/performance')
def admin_performance():
    if 'email' not in session or session['role'] != 'admin':
         return redirect(url_for('login'))
         
    engineer_stats = get_engineer_stats(session.get('company'))
    return render_template('admin_performance.html', engineer_stats=engineer_stats)

@app.route('/admin/incidents/<filter_type>')
def admin_incidents(filter_type):
    if 'email' not in session or session['role'] != 'admin':
         return redirect(url_for('login'))
         
    incidents = get_incidents_filtered(filter_type, session.get('company'))
    
    # Map filter type to a readable title
    titles = {
        'total': 'Total Incidents',
        'high': 'High Priority Incidents',
        'medium': 'Medium Priority Incidents',
        'low': 'Low Priority Incidents',
        'open': 'Open Incidents',
        'escalated': 'Escalated Incidents',
        'major': 'Major Incidents'
    }
    title = titles.get(filter_type, 'Incidents')
    
    return render_template('admin_list_view.html', incidents=incidents, title=title, filter_type=filter_type)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
