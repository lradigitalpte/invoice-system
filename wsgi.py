"""
WSGI entry point for production deployment on Heroku
"""
from dotenv import load_dotenv
import os

# Load environment variables from .env if it exists locally
load_dotenv('.env')
load_dotenv('.env.local')

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
