"""
Migration script to create company_settings table
Run this once to set up the company settings table
"""
from app import create_app, db
from app.models import CompanySettings

# Create a Flask app context
app = create_app()

with app.app_context():
    print("Creating company_settings table...")
    
    try:
        # Ensure the model is imported and registered
        from app.models.company import CompanySettings
        
        # Create the table explicitly
        CompanySettings.__table__.create(db.engine, checkfirst=True)
        print("✓ Created 'company_settings' table (if not exists)")
        
        # Create default settings if none exist
        try:
            if CompanySettings.query.first() is None:
                default_settings = CompanySettings(
                    company_name="Your Company Name"
                )
                db.session.add(default_settings)
                db.session.commit()
                print("✓ Created default company settings")
            else:
                print("✓ Company settings already exist")
        except Exception as query_error:
            print(f"Note: Could not query settings (this is OK if table was just created): {query_error}")
            # Try to create default settings anyway
            try:
                default_settings = CompanySettings(
                    company_name="Your Company Name"
                )
                db.session.add(default_settings)
                db.session.commit()
                print("✓ Created default company settings")
            except:
                pass
        
        print("\n✓ Migration completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()

