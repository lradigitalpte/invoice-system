from app import db
from datetime import datetime

class Quotation(db.Model):
    __tablename__ = 'quotations'
    
    id = db.Column(db.Integer, primary_key=True)
    quotation_number = db.Column(db.String(50), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, expired
    notes = db.Column(db.Text)
    terms = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = db.relationship('QuotationItem', backref='quotation', lazy=True, cascade='all, delete-orphan')
    client = db.relationship('Client', backref='quotations', lazy=True)
    
    def get_total(self):
        return sum(item.total for item in self.items)
    
    def to_dict(self):
        return {
            'id': self.id,
            'quotation_number': self.quotation_number,
            'client_id': self.client_id,
            'client_name': self.client.name,
            'issue_date': self.issue_date.isoformat(),
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'status': self.status,
            'total': self.get_total(),
            'notes': self.notes,
            'terms': self.terms,
            'created_at': self.created_at.isoformat()
        }


class QuotationItem(db.Model):
    __tablename__ = 'quotation_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotations.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    tax_rate = db.Column(db.Float, default=0)
    
    @property
    def subtotal(self):
        return self.quantity * self.unit_price
    
    @property
    def tax(self):
        return self.subtotal * (self.tax_rate / 100)
    
    @property
    def total(self):
        return self.subtotal + self.tax
    
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'tax_rate': self.tax_rate,
            'subtotal': self.subtotal,
            'tax': self.tax,
            'total': self.total
        }
