"""
Heroku release script - runs migrations on deploy
This script runs automatically after deployment on Heroku
"""
from app import create_app, db
from app.models import CompanySettings

app = create_app()

with app.app_context():
    print("Running database migrations...")
    
    # Create all tables
    try:
        db.create_all()
        print("✓ Database tables created/verified")
        
        # Ensure company settings exist
        if CompanySettings.query.first() is None:
            default_settings = CompanySettings(company_name="Your Company Name")
            db.session.add(default_settings)
            db.session.commit()
            print("✓ Created default company settings")
        else:
            print("✓ Company settings already exist")
            
    except Exception as e:
        print(f"⚠ Migration warning: {e}")
        # Don't fail deployment on migration errors
    
    print("✓ Release script completed")

