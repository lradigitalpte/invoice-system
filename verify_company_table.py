"""
Script to verify and create company_settings table if needed
"""
from app import create_app, db
from app.models import CompanySettings
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    print("Checking company_settings table...")
    
    # Check if table exists
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'company_settings' in tables:
        print("✓ Table 'company_settings' exists")
        
        # Check if there's a record
        try:
            settings = CompanySettings.query.first()
            if settings:
                print(f"✓ Company settings found: {settings.company_name}")
            else:
                print("⚠ Table exists but no settings record found. Creating default...")
                default_settings = CompanySettings(company_name="Your Company Name")
                db.session.add(default_settings)
                db.session.commit()
                print("✓ Created default company settings")
        except Exception as e:
            print(f"⚠ Error querying table: {e}")
            print("Attempting to create table...")
            try:
                CompanySettings.__table__.create(db.engine, checkfirst=True)
                print("✓ Table created successfully")
            except Exception as create_error:
                print(f"✗ Error creating table: {create_error}")
    else:
        print("✗ Table 'company_settings' does NOT exist")
        print("Creating table...")
        try:
            CompanySettings.__table__.create(db.engine, checkfirst=True)
            print("✓ Table created successfully")
            
            # Create default settings
            default_settings = CompanySettings(company_name="Your Company Name")
            db.session.add(default_settings)
            db.session.commit()
            print("✓ Created default company settings")
        except Exception as e:
            print(f"✗ Error creating table: {e}")
            import traceback
            traceback.print_exc()

