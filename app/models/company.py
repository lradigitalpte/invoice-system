from app import db
from datetime import datetime

class CompanySettings(db.Model):
    __tablename__ = 'company_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False, default='Your Company Name')
    company_address = db.Column(db.Text)
    company_city = db.Column(db.String(100))
    company_state = db.Column(db.String(100))
    company_zip = db.Column(db.String(20))
    company_country = db.Column(db.String(100))
    company_phone = db.Column(db.String(50))
    company_email = db.Column(db.String(200))
    company_website = db.Column(db.String(200))
    company_tax_id = db.Column(db.String(100))
    
    # Payment details
    bank_name = db.Column(db.String(200))
    bank_account_number = db.Column(db.String(100))
    bank_routing_number = db.Column(db.String(100))
    bank_swift_code = db.Column(db.String(50))
    payment_instructions = db.Column(db.Text)
    payment_methods = db.Column(db.Text)  # JSON string or comma-separated
    
    # Logo
    logo_filename = db.Column(db.String(255))
    logo_path = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_settings(cls):
        """Get or create company settings (singleton pattern)"""
        settings = cls.query.first()
        if not settings:
            settings = cls()
            db.session.add(settings)
            db.session.commit()
        return settings
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'company_address': self.company_address,
            'company_city': self.company_city,
            'company_state': self.company_state,
            'company_zip': self.company_zip,
            'company_country': self.company_country,
            'company_phone': self.company_phone,
            'company_email': self.company_email,
            'company_website': self.company_website,
            'company_tax_id': self.company_tax_id,
            'bank_name': self.bank_name,
            'bank_account_number': self.bank_account_number,
            'bank_routing_number': self.bank_routing_number,
            'bank_swift_code': self.bank_swift_code,
            'payment_instructions': self.payment_instructions,
            'payment_methods': self.payment_methods,
            'logo_filename': self.logo_filename,
            'logo_path': self.logo_path
        }

