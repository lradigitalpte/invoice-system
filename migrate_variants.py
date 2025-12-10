#!/usr/bin/env python
"""Migration script to add product variations support"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
except ImportError:
    pass

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        print("Starting migration...")
        
        try:
            # Add has_variants column to products table
            print("Adding 'has_variants' column to products table...")
            try:
                db.session.execute(text("ALTER TABLE products ADD COLUMN has_variants BOOLEAN DEFAULT FALSE"))
                db.session.commit()
                print("✓ Added 'has_variants' column")
            except Exception as e:
                if "Duplicate column name" in str(e) or "already exists" in str(e).lower():
                    print("  'has_variants' column already exists, skipping...")
                else:
                    raise
            
            # Create product_options table
            print("Creating 'product_options' table...")
            try:
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS product_options (
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        product_id INTEGER NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        display_order INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                    )
                """))
                db.session.commit()
                print("✓ Created 'product_options' table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("  'product_options' table already exists, skipping...")
                else:
                    raise
            
            # Create product_option_values table
            print("Creating 'product_option_values' table...")
            try:
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS product_option_values (
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        option_id INTEGER NOT NULL,
                        value VARCHAR(100) NOT NULL,
                        display_order INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (option_id) REFERENCES product_options(id) ON DELETE CASCADE
                    )
                """))
                db.session.commit()
                print("✓ Created 'product_option_values' table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("  'product_option_values' table already exists, skipping...")
                else:
                    raise
            
            # Create product_variants table
            print("Creating 'product_variants' table...")
            try:
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS product_variants (
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        product_id INTEGER NOT NULL,
                        sku VARCHAR(100) UNIQUE,
                        price FLOAT NOT NULL,
                        tax_rate FLOAT,
                        is_active BOOLEAN DEFAULT TRUE,
                        variant_data TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                    )
                """))
                db.session.commit()
                print("✓ Created 'product_variants' table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("  'product_variants' table already exists, skipping...")
                else:
                    raise
            
            # Update existing products to have has_variants = False
            print("Updating existing products...")
            try:
                db.session.execute(text("UPDATE products SET has_variants = FALSE WHERE has_variants IS NULL"))
                db.session.commit()
                print("✓ Updated existing products")
            except Exception as e:
                print(f"  Note: {e}")
            
            print("\n✓ Migration completed successfully!")
            
        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            db.session.rollback()
            raise

