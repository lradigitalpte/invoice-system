from app import create_app
from dotenv import load_dotenv
import os

# Load environment variables from .env.local
load_dotenv('.env.local')

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='localhost', port=5000)
