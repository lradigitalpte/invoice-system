from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    sku = db.Column(db.String(100), unique=True)
    price = db.Column(db.Float, nullable=False)
    tax_rate = db.Column(db.Float, default=0)
    category = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'sku': self.sku,
            'price': self.price,
            'tax_rate': self.tax_rate,
            'category': self.category,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
