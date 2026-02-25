# AI-Based IT Incident Management System

A web-based application for managing IT incidents with AI-powered prioritization and resolution tracking.

## Features
- **AI Prioritization**: Automatically discriminates between High, Medium, and Low urgency using NLP.
- **Major Incident Detection**: Identifies similar open tickets to flag potential major outages.
- **Role-Based Access**:
  - **Employee**: Submit and view own tickets.
  - **Support**: View all tickets, pick them, and resolve them.
  - **Admin**: Overview stats and all tickets.
- **Modern UI**: Response glassmorphism design with dark mode.

## Prerequisites
- Python 3.8+
- MongoDB (running on localhost:27017)

## Setup
1. **Install Dependencies**:
   ```bash
   pip install flask pymongo scikit-learn nltk
   ```
2. **Setup Database**:
   Ensure MongoDB service is running. The app will automatically create the database `incident_db` on first run.

3. **Run the Application**:
   - **Method A (Terminal)**:
     ```bash
     cd backend
     python app.py
     ```
   - **Method B (VS Code)**:
     - Open the file `backend/app.py`.
     - Click the "Run" button (Play icon) in the top right corner.
     - Or press `F5` to start debugging.

4. **Access**:
   Open browser at `http://localhost:5000`.

## Usage Guide
1. **Register**: Create an account (choose Role: Employee, Support, or Admin).
2. **Submit Incident** (Employee): Type a description.
   - Try words like "outage", "critical" to see High priority.
   - Try "slow", "glitch" for Medium.
   - Try "typo" for Low.
3. **Manage** (Support/Admin): Log in to see the dashboard and resolve tickets.

## Technical Details
- **Backend**: Flask (Python)
- **Database**: MongoDB
- **AI**: TF-IDF + Cosine Similarity (Scikit-Learn) for grouping; Keyword rules for priority.
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript.
