from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    sku = db.Column(db.String(100), unique=True, nullable=True)  # Base SKU, can be null if only variants have SKUs
    price = db.Column(db.Float, nullable=False)  # Base price, variants can override
    tax_rate = db.Column(db.Float, default=0)
    category = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    has_variants = db.Column(db.Boolean, default=False)  # Whether this product has variations
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    options = db.relationship('ProductOption', backref='product', lazy=True, cascade='all, delete-orphan')
    variants = db.relationship('ProductVariant', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def get_default_price(self):
        """Get the default price (from variants if exists, else base price)"""
        if self.has_variants and self.variants:
            # Return first variant price as default
            return self.variants[0].price if self.variants else self.price
        return self.price
    
    def get_default_sku(self):
        """Get the default SKU (from variants if exists, else base SKU)"""
        if self.has_variants and self.variants:
            return self.variants[0].sku if self.variants and self.variants[0].sku else self.sku
        return self.sku
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'sku': self.get_default_sku(),
            'price': self.get_default_price(),
            'tax_rate': self.tax_rate,
            'category': self.category,
            'is_active': self.is_active,
            'has_variants': self.has_variants,
            'variants_count': len(self.variants) if self.variants else 0,
            'created_at': self.created_at.isoformat()
        }


class ProductOption(db.Model):
    """Represents a variation type (e.g., Version, Model, Configuration)"""
    __tablename__ = 'product_options'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Version", "Model", "Configuration"
    display_order = db.Column(db.Integer, default=0)  # Order of display
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to option values
    values = db.relationship('ProductOptionValue', backref='option', lazy=True, cascade='all, delete-orphan', order_by='ProductOptionValue.display_order')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_order': self.display_order,
            'values': [v.to_dict() for v in self.values]
        }


class ProductOptionValue(db.Model):
    """Represents a value for an option (e.g., "Basic", "Pro", "Advanced" for Version)"""
    __tablename__ = 'product_option_values'
    
    id = db.Column(db.Integer, primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey('product_options.id'), nullable=False)
    value = db.Column(db.String(100), nullable=False)  # e.g., "Basic", "Pro", "Advanced"
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'display_order': self.display_order
        }


class ProductVariant(db.Model):
    """Represents a specific combination of option values (e.g., Version=Pro, Model=Premium)"""
    __tablename__ = 'product_variants'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=True)
    price = db.Column(db.Float, nullable=False)
    tax_rate = db.Column(db.Float, nullable=True)  # Can override product tax rate
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Store variant attributes as JSON (e.g., {"Version": "Pro", "Model": "Premium"})
    variant_data = db.Column(db.Text)  # JSON string of option values
    
    def get_variant_display_name(self):
        """Get a display name for this variant (e.g., "Pro - Premium")"""
        if not self.variant_data:
            return self.product.name
        try:
            import json
            data = json.loads(self.variant_data)
            parts = [f"{k}: {v}" for k, v in data.items()]
            return " - ".join(parts)
        except:
            return self.product.name
    
    def get_variant_label(self):
        """Get a short label (e.g., "Pro - Premium")"""
        return self.get_variant_display_name()
    
    def to_dict(self):
        variant_data = {}
        if self.variant_data:
            try:
                import json
                variant_data = json.loads(self.variant_data)
            except:
                pass
        
        return {
            'id': self.id,
            'product_id': self.product_id,
            'sku': self.sku,
            'price': self.price,
            'tax_rate': self.tax_rate or self.product.tax_rate,
            'is_active': self.is_active,
            'variant_data': variant_data,
            'display_name': self.get_variant_display_name()
        }
