# Flask Application Project

A simple Flask web application with SQLite database, designed for Apache2 deployment with reverse proxy.

## Features

- **Flask Web Framework** - Python-based web framework
- **SQLite Database** - Simple file-based database with direct SQL queries
- **No ORM** - Direct database connections and raw SQL queries (no SQLAlchemy)
- **User Management** - Create and manage users
- **Post Management** - Create and manage posts
- **RESTful API** - JSON endpoints for users and posts
- **Apache2 Ready** - Configured for Apache2 reverse proxy deployment
- **Responsive Design** - Modern, responsive HTML templates

## Project Structure

```
flask_app/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── database.py          # Database connection management
│   ├── routes.py            # Route handlers (web and API)
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Stylesheet
│   │   └── js/              # JavaScript files
│   └── templates/
│       ├── base.html        # Base template
│       ├── index.html       # Home page
│       ├── users.html       # Users list
│       ├── add_user.html    # Add user form
│       ├── user_detail.html # User details
│       ├── posts.html       # Posts list
│       ├── add_post.html    # Add post form
│       └── error.html       # Error page
├── database/                # Database directory
├── config.py                # Configuration settings
├── run.py                   # Development server entry point
├── wsgi.py                  # WSGI entry point for Apache2
├── apache2_config.conf      # Apache2 virtual host configuration
├── gunicorn_config.py       # Gunicorn WSGI server config (optional)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

### 1. Create Virtual Environment (Optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
python run.py
```

Or use Flask CLI:

```bash
export FLASK_APP=app
flask init-db
```

## Running the Application

### Development Server

```bash
python run.py
```

The application will be available at `http://127.0.0.1:5000`

### Production Server with Gunicorn

Install gunicorn (optional):

```bash
pip install gunicorn
```

Run with gunicorn:

```bash
gunicorn -c gunicorn_config.py wsgi:app
```

## Apache2 Deployment

### 1. Install Apache Modules

```bash
sudo apt-get update
sudo apt-get install apache2
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod rewrite
sudo a2enmod headers
```

### 2. Configure Virtual Host

Copy the Apache configuration:

```bash
sudo cp apache2_config.conf /etc/apache2/sites-available/flask_app.conf
```

Edit the configuration to match your setup:

```bash
sudo nano /etc/apache2/sites-available/flask_app.conf
```

### 3. Enable Virtual Host

```bash
sudo a2ensite flask_app
sudo apache2ctl configtest
sudo systemctl restart apache2
```

### 4. Run Flask Application

```bash
# Development
python run.py

# Or Production with Gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app
```

### Alternative: Direct mod_wsgi Deployment

Uncomment the mod_wsgi section in `apache2_config.conf` and install:

```bash
sudo apt-get install libapache2-mod-wsgi-py3
sudo a2enmod wsgi
```

## Database

### Tables

**users**
- id (INTEGER PRIMARY KEY)
- username (TEXT UNIQUE)
- email (TEXT UNIQUE)
- created_at (TIMESTAMP)

**posts**
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER FOREIGN KEY)
- title (TEXT)
- content (TEXT)
- created_at (TIMESTAMP)

### Direct Database Query

The application uses direct SQLite queries. Example from `routes.py`:

```python
db = get_db()
db.execute('INSERT INTO users (username, email) VALUES (?, ?)', (username, email))
db.commit()
```

## API Endpoints

### Users
- `GET /api/users` - List all users
- `GET /api/users/<id>` - Get user by ID

### Posts
- `GET /api/posts` - List all posts
- `GET /api/posts/<id>` - Get post by ID

## Configuration

Edit `config.py` to customize:

```python
class Config:
    SECRET_KEY = 'your-secret-key'
    DATABASE = 'path/to/database.db'
    DEBUG = False
```

Environment variables:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
export SECRET_KEY=your-secret-key
```

## File Locations

- **Database**: `database/app.db`
- **Static files**: `app/static/`
- **Templates**: `app/templates/`
- **Logs** (Apache2): `/var/log/apache2/flask_app_*.log`

## Common Tasks

### Adding a New Route

Edit `app/routes.py`:

```python
@main_bp.route('/new-route')
def new_route():
    db = get_db()
    # Your code here
    return render_template('template.html')
```

### Querying the Database

```python
db = get_db()

# SELECT
cursor = db.execute('SELECT * FROM users WHERE id = ?', (1,))
user = cursor.fetchone()

# INSERT
db.execute('INSERT INTO users (username, email) VALUES (?, ?)', ('john', 'john@example.com'))
db.commit()

# UPDATE
db.execute('UPDATE users SET email = ? WHERE id = ?', ('newemail@example.com', 1))
db.commit()

# DELETE
db.execute('DELETE FROM users WHERE id = ?', (1,))
db.commit()
```

## Security Notes

⚠️ **This template uses direct SQL queries without parameterization for demonstration purposes.** The `?` placeholders in queries are for SQLite parameter binding, but this project intentionally does NOT use prepared statements or ORM for educational/demonstration purposes.

For production use, always:
- Use parameterized queries (which this template does)
- Validate and sanitize user input
- Use HTTPS with Apache2
- Set strong SECRET_KEY
- Use environment variables for sensitive data
- Keep Flask and dependencies updated

## Troubleshooting

### Port Already in Use

If port 5000 is in use, change in `run.py`:

```python
app.run(host='127.0.0.1', port=8000, debug=True)
```

### Database Locked

Close other connections and clear any `.db-journal` files.

### Apache2 Module Issues

Check Apache configuration:

```bash
sudo apache2ctl configtest
```

View logs:

```bash
sudo tail -f /var/log/apache2/error.log
```

## Requirements

- Python 3.6+
- Flask 3.0.0
- Apache2 (for production)
- mod_proxy (for reverse proxy)

## License

This is a template project for learning purposes.
