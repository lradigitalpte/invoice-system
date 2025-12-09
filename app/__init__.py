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
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from app.routes import clients, invoices, payments, products, quotations
    app.register_blueprint(clients.bp)
    app.register_blueprint(invoices.bp)
    app.register_blueprint(payments.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(quotations.bp)

    # Root route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app
