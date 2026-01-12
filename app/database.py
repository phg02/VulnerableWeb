import sqlite3
from flask import g, current_app
import os

def get_db():
    """Get database connection"""
    if 'db' not in g:
        db_path = current_app.config['DATABASE']
        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with schema"""
    db = get_db()
    # Create users table with required columns (plaintext password for this lab)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    
    # Create todos table (shared among all users)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    db.commit()
    print("Database initialized successfully")

def seed_admin():
    """Seed an admin account"""
    db = get_db()
    try:
        # Insert admin account if it doesn't exist
        db.execute(
            """
            INSERT INTO users (username, email, password, role)
            VALUES (?, ?, ?, ?)
            """,
            ('admin', 'admin@example.com', 'admin123', 'admin')
        )
        db.commit()
        print("Admin account created successfully: admin / admin123")
    except sqlite3.IntegrityError:
        print("Admin account already exists")
