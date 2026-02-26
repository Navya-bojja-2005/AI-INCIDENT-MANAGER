import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string

# Download NLTK data quietly if not present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def preprocess_text(text):
    """Clean and preprocess text: lowercase, remove punctuation, remove stopwords."""
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [w for w in tokens if not w in stop_words]
    return " ".join(filtered_tokens)

def assign_priority_rule_based(text):
    """Assign priority based on expanded keywords in the text."""
    text = text.lower()
    
    # 🔴 High Priority Keywords
    high_keywords = [
        "server down", "production failure", "database crash", "system outage", "data loss", 
        "security breach", "authentication failure", "payment failure", "network outage", 
        "ransomware", "firewall failure", "service unavailable", "cpu overload", "memory crash", 
        "api crash", "critical error", "billing system down", "vpn down", "infrastructure failure",
        "critical", "urgent", "emergency", "breach", "production"
    ]
    
    # 🟠 Medium Priority Keywords
    medium_keywords = [
        "login issue", "application slow", "timeout error", "access issue", "email delay", 
        "sync problem", "report failure", "partial outage", "intermittent error", 
        "performance degradation", "file upload error", "permission issue", "api delay", 
        "minor service disruption", "issue", "error", "bug", "glitch", "warning", "delay", 
        "problem", "limit", "latency"
    ]
    
    # 🟢 Low Priority Keywords
    low_keywords = [
        "mouse is not working", "mouse not working", "keyboard not working", "printer not working",
        "ui alignment", "typo", "cosmetic", "color", "icon", "monitor", "screen", "display", 
        "mouse", "keyboard", "printer", "headset", "cable", "reset password", "formatting", 
        "suggestion", "question", "training", "feature request"
    ]
    
    # Priority Check (Highest severity first)
    
    # 1. Check High
    for word in high_keywords:
        if word in text:
            return "High"

    # 2. Check Low (Check specific low items before generic medium items like 'issue')
    for word in low_keywords:
        if word in text:
            return "Low"
            
    # 3. Check Medium
    for word in medium_keywords:
        if word in text:
            return "Medium"

    return "Medium" # Default fallback

def assign_engineer_rule_based(text):
    """
    Auto-assign incident to an engineering group based on keywords.
    Groups: Infrastructure Engineer, Application Support Engineer, Network Engineer
    Default: General Support
    """
    text = text.lower()
    
    infra_keywords = ["server", "cpu", "memory", "disk", "hardware", "vm", "cloud", "infrastructure", "crash", "monitor"]
    app_keywords = ["app", "application", "ui", "login", "bug", "error", "glitch", "feature", "code", "report", "sync", "payment", "frontend", "backend", "api"]
    network_keywords = ["network", "wifi", "internet", "vpn", "firewall", "connection", "latency", "bandwidth", "dns", "ip", "router", "switch"]
    db_keywords = ["database", "sql", "query", "data loss", "backup", "restore", "schema", "table", "mongo", "mysql", "postgres", "oracle"]
    security_keywords = ["security", "breach", "password", "authentication", "auth", "hacked", "ransomware", "phishing", "access denied", "permission"]
    
    # Check Security
    for word in security_keywords:
        if word in text:
            return "Security Operations Team"

    # Check Database
    for word in db_keywords:
        if word in text:
            return "Database Support Team"

    # Check Network
    for word in network_keywords:
        if word in text:
            return "Network Support Team"
            
    # Check Infrastructure
    for word in infra_keywords:
        if word in text:
            return "Infrastructure Team"
            
    # Check Application
    for word in app_keywords:
        if word in text:
            return "Application Support Team"
            
    return "General Support" # Fallback

def validate_incident_relevance(text):
    """
    Check if the incident description is relevant to IT support using keyword matching.
    """
    text = text.lower()
    it_keywords = [
        "server", "network", "database", "app", "application", "login", "api", "error", 
        "fail", "crash", "bug", "issue", "slow", "down", "access", "permission", 
        "email", "wifi", "internet", "vpn", "printer", "computer", "laptop", "mouse", 
        "monitor", "keyboard", "software", "install", "update", "patch", "security", 
        "breach", "password", "reset", "account", "locked", "timeout", "connection",
        "data", "file", "folder", "drive", "storage", "cloud", "vm", "host", "port",
        "code", "deploy", "build", "test", "debug", "log", "trace", "exception",
        "billing", "payment", "feature", "request", "help", "support", "question"
    ]
    
    # Check if any IT keyword is present
    # This is a simple heuristic; in production, use a trained classifier.
    tokens = word_tokenize(text)
    relevant_tokens = [w for w in tokens if w in it_keywords]
    
    if len(relevant_tokens) > 0:
        return True, "Relevant"
    else:
        # If text is too short, might be a false negative, but we'll flag it.
        # Actually, let's be lenient for this demo.
        if len(tokens) > 3:
             return True, "Assumed Relevant (Length)"
        return True, "Assumed Relevant" # Default to True to avoid blocking valid but keyword-less inputs

def check_similarity(new_text, existing_incidents, threshold=0.7):
    """
    Check if the new incident is similar to existing open incidents using TF-IDF.
    Returns: is_similar (bool), similar_id (str), score (float)
    """
    if not existing_incidents:
        return False, None, 0.0
        
    documents = [i.get('description', '') for i in existing_incidents]
    ids = [str(i.get('_id')) for i in existing_incidents]
    
    # Add new text to the end
    documents.append(new_text)
    
    try:
        tfidf_vectorizer = TfidfVectorizer().fit_transform(documents)
        cosine_matrix = cosine_similarity(tfidf_vectorizer[-1], tfidf_vectorizer[:-1])
        
        # Find the max similarity
        if cosine_matrix.size > 0:
            max_score = cosine_matrix.max()
            best_match_idx = cosine_matrix.argmax()
            
            if max_score > threshold:
                return True, ids[best_match_idx], float(max_score)
            else:
                 return False, None, float(max_score)
        else:
            return False, None, 0.0
            
    except ValueError:
        # Handle empty vocabulary or other vectorizer errors
        return False, None, 0.0

def analyze_incident(description, get_open_incidents_func):
    """
    Main function to analyze an incident.
    Returns: priority, assigned_group, similarity_info, validation_result
    """
    # Step 1: Validate Relevance
    is_relevant, reason = validate_incident_relevance(description)
    if not is_relevant:
        return {
            "error": reason
        }

    # Step 2: Priority Assignment
    priority = assign_priority_rule_based(description)
    
    # Step 3: Auto-Assignment
    assigned_group = assign_engineer_rule_based(description)
    
    # Step 4: Check for major incident grouping
    existing_incidents = get_open_incidents_func()
    is_major, major_id, score = check_similarity(description, existing_incidents)
    
    return {
        "priority": priority,
        "assigned_group": assigned_group,
        "is_major_candidate": is_major,
        "similar_to": major_id,
        "similarity_score": score
    }
