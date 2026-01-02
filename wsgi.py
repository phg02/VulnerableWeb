"""
WSGI entry point for Apache2 deployment
This file is used by mod_wsgi to run the Flask application
"""
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

# Create the Flask app instance
app = create_app()

# Initialize database on startup
with app.app_context():
    from app.database import get_db, init_db
    try:
        get_db()
        init_db()
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == '__main__':
    app.run()
    
application = app
