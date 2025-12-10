from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuration for MySQL with XAMPP or production database
    database_url = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/invoice')
    
    # Heroku uses postgres:// but SQLAlchemy needs postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Connection pooling and timeout settings for better MySQL reliability
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,  # Recycle connections every hour
        'pool_pre_ping': True,  # Test connections before using them
        'connect_args': {
            'charset': 'utf8mb4',
            'read_timeout': 30,
            'write_timeout': 30,
        }
    }
    
    # Initialize database
    db.init_app(app)
    
    # Import all models to ensure they're registered with SQLAlchemy before creating tables
    # This must be done before db.create_all() is called
    with app.app_context():
        # Import all models to register them with SQLAlchemy
        from app.models import CompanySettings, Client, Invoice, InvoiceItem, Payment, Product, Quotation, QuotationItem
        # Now create all tables
        db.create_all()
    
    # Register blueprints
    from app.routes import clients, invoices, payments, products, quotations, settings
    app.register_blueprint(clients.bp)
    app.register_blueprint(invoices.bp)
    app.register_blueprint(payments.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(quotations.bp)
    app.register_blueprint(settings.bp)

    # Root route
    @app.route('/')
    def index():
        from app.models import Invoice, Client
        from sqlalchemy import func
        
        # Get statistics
        total_invoices = db.session.query(func.count(Invoice.id)).scalar() or 0
        total_clients = db.session.query(func.count(Client.id)).scalar() or 0
        
        # Get pending invoices
        pending_invoices = db.session.query(func.count(Invoice.id)).filter(
            Invoice.status.in_(['draft', 'sent'])
        ).scalar() or 0
        
        # Get total revenue from paid invoices
        try:
            paid_invoices = Invoice.query.filter_by(status='paid').all()
            total_revenue = sum(inv.get_total() for inv in paid_invoices) if paid_invoices else 0
        except:
            total_revenue = 0
        
        # Get recent invoices
        recent_invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(5).all()
        
        stats = {
            'total_invoices': total_invoices,
            'total_clients': total_clients,
            'total_revenue': f"${total_revenue:,.2f}" if total_revenue > 0 else "$0.00",
            'pending_invoices': pending_invoices,
            'recent_invoices': recent_invoices
        }
        
        return render_template('index.html', stats=stats)
    
    return app
