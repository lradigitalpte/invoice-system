#!/usr/bin/env python
"""Database initialization script"""

from dotenv import load_dotenv
from app import create_app, db

# Load environment variables from .env.local
load_dotenv('.env.local')

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
