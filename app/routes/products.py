from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app import db
from app.models import Product
from datetime import datetime

bp = Blueprint('products', __name__, url_prefix='/products')

@bp.route('/')
def list_products():
    category_filter = request.args.get('category', 'all')
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = Product.query
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    
    products = query.paginate(page=page, per_page=20)
    categories = db.session.query(Product.category).distinct().all()
    return render_template('products/list.html', products=products, categories=[c[0] for c in categories if c[0]], category_filter=category_filter, status_filter=status_filter)

@bp.route('/new', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        product = Product(
            name=request.form.get('name'),
            description=request.form.get('description'),
            sku=request.form.get('sku'),
            price=float(request.form.get('price')),
            tax_rate=float(request.form.get('tax_rate') or 0),
            category=request.form.get('category'),
            is_active=request.form.get('is_active') == 'on'
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('products.list_products'))
    
    return render_template('products/form.html', product=None)

@bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.sku = request.form.get('sku')
        product.price = float(request.form.get('price'))
        product.tax_rate = float(request.form.get('tax_rate') or 0)
        product.category = request.form.get('category')
        product.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        return redirect(url_for('products.list_products'))
    
    return render_template('products/form.html', product=product)

@bp.route('/<int:product_id>/delete', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('products.list_products'))

@bp.route('/api/list')
def api_list_products():
    products = Product.query.filter_by(is_active=True).all()
    return jsonify([product.to_dict() for product in products])

@bp.route('/api/search')
def api_search_products():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    products = Product.query.filter(
        db.and_(
            Product.is_active == True,
            db.or_(
                Product.name.ilike(f'%{query}%'),
                Product.description.ilike(f'%{query}%'),
                Product.sku.ilike(f'%{query}%')
            )
        )
    ).limit(10).all()
    
    return jsonify([product.to_dict() for product in products])

