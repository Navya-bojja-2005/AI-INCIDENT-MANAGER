# Data Location

The application uses **MongoDB** for data storage.

- **Database Name**: `incident_db`
- **Collections**:
    - `users`: Stores user registration data (email, password, role).
    - `incidents`: Stores incident tickets (description, priority, status, etc.).

## Accessing Data
You can access the data using MongoDB Compass or the CLI:

```bash
mongosh
use incident_db
db.users.find().pretty()
db.incidents.find().pretty()
```
