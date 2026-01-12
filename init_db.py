#!/usr/bin/env python3
"""Initialize and seed the database"""
import os
import sys

# Add the project to the path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.database import init_db, seed_admin, get_db

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Initialize database schema
        init_db()
        # Seed admin account
        seed_admin()
        print("\nDatabase setup complete!")
        print("Admin credentials:")
        print("  Username: admin")
        print("  Password: admin123")
