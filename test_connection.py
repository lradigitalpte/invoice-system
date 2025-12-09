#!/usr/bin/env python
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env.local
load_dotenv('.env.local')

database_url = os.environ.get('DATABASE_URL')
print(f"Database URL loaded: {database_url}")

# Try to import and connect
try:
    from sqlalchemy import create_engine, text
    print("\nAttempting to connect to database...")
    
    engine = create_engine(database_url, echo=False)
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✓ Successfully connected to Clever Cloud database!")
        print(f"✓ Connection test result: {result.fetchone()}")
        
except Exception as e:
    print(f"✗ Connection failed: {type(e).__name__}: {e}")
    sys.exit(1)
