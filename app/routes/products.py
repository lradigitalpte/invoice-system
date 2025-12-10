from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app import db
from app.models import Product, ProductOption, ProductOptionValue, ProductVariant
from datetime import datetime
import json
from itertools import product as itertools_product

bp = Blueprint('products', __name__, url_prefix='/products')

@bp.route('/')
def list_products():
    category_filter = request.args.get('category', 'all')
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'name')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate per_page to prevent abuse
    if per_page not in [5, 10, 25, 50, 100]:
        per_page = 10
    
    query = Product.query
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    
    if search:
        if search_by == 'name':
            query = query.filter(Product.name.ilike(f'%{search}%'))
        elif search_by == 'product_id':
            try:
                query = query.filter(Product.id == int(search))
            except:
                pass
        elif search_by == 'sku':
            query = query.filter(Product.sku.ilike(f'%{search}%'))
    
    products = query.order_by(Product.name).paginate(page=page, per_page=per_page, error_out=False)
    categories = db.session.query(Product.category).distinct().all()
    return render_template('products/list.html', products=products, categories=[c[0] for c in categories if c[0]], category_filter=category_filter, status_filter=status_filter, search=search, search_by=search_by, per_page=per_page)

@bp.route('/new', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        has_variants = request.form.get('has_variants') == 'on'
        
        # Auto-generate SKU if not provided
        sku = request.form.get('sku') or None
        if not sku:
            # Generate SKU from product name
            name = request.form.get('name', '').strip()
            if name:
                # Create SKU from name: uppercase, remove special chars, limit to 20 chars
                sku_base = ''.join(c.upper() if c.isalnum() else '' for c in name)[:15]
                # Add number suffix if needed to make unique
                counter = 1
                sku = f"{sku_base}{counter:03d}"
                while Product.query.filter_by(sku=sku).first():
                    counter += 1
                    sku = f"{sku_base}{counter:03d}"
        
        product = Product(
            name=request.form.get('name'),
            description=request.form.get('description'),
            sku=sku,
            price=float(request.form.get('price')),
            tax_rate=float(request.form.get('tax_rate') or 0),
            category=request.form.get('category'),
            is_active=request.form.get('is_active') == 'on',
            has_variants=has_variants
        )
        db.session.add(product)
        db.session.flush()
        
        # Handle variations if enabled
        if has_variants:
            # Get option names and values from form
            option_names = request.form.getlist('option_name[]')
            option_values_list = request.form.getlist('option_values[]')
            
            # Create options and values
            options = []
            for idx, option_name in enumerate(option_names):
                if option_name.strip():
                    option = ProductOption(
                        product_id=product.id,
                        name=option_name.strip(),
                        display_order=idx
                    )
                    db.session.add(option)
                    db.session.flush()
                    
                    # Parse values (comma-separated)
                    values_str = option_values_list[idx] if idx < len(option_values_list) else ''
                    values = [v.strip() for v in values_str.split(',') if v.strip()]
                    
                    for val_idx, value in enumerate(values):
                        option_value = ProductOptionValue(
                            option_id=option.id,
                            value=value,
                            display_order=val_idx
                        )
                        db.session.add(option_value)
                    
                    options.append(option)
            
            # Generate all variant combinations
            if options:
                # Get all value combinations
                all_value_combos = []
                for option in options:
                    values = [v.value for v in option.values]
                    all_value_combos.append(values)
                
                # Generate cartesian product of all combinations
                variant_combinations = list(itertools_product(*all_value_combos))
                
                # Create variants
                base_price = float(request.form.get('price'))
                variant_prices = request.form.getlist('variant_price[]')
                variant_skus = request.form.getlist('variant_sku[]')
                
                for idx, combo in enumerate(variant_combinations):
                    # Create variant data dict
                    variant_data = {}
                    for opt_idx, option in enumerate(options):
                        variant_data[option.name] = combo[opt_idx]
                    
                    # Get price for this variant (or use base price)
                    variant_price = float(variant_prices[idx]) if idx < len(variant_prices) and variant_prices[idx] else base_price
                    variant_sku = variant_skus[idx] if idx < len(variant_skus) and variant_skus[idx] else None
                    
                    # Auto-generate variant SKU if not provided
                    if not variant_sku:
                        base_sku = product.sku or f"PROD{product.id:05d}"
                        variant_suffix = "-".join([str(v).upper()[:3] for v in combo])
                        variant_sku = f"{base_sku}-{variant_suffix}"
                        # Ensure uniqueness
                        counter = 1
                        original_sku = variant_sku
                        while ProductVariant.query.filter_by(sku=variant_sku).first():
                            variant_sku = f"{original_sku}-{counter}"
                            counter += 1
                    
                    variant = ProductVariant(
                        product_id=product.id,
                        sku=variant_sku,
                        price=variant_price,
                        tax_rate=float(request.form.get('tax_rate') or 0),
                        variant_data=json.dumps(variant_data),
                        is_active=True
                    )
                    db.session.add(variant)
        
        db.session.commit()
        return redirect(url_for('products.list_products'))
    
    # Get existing categories for dropdown suggestions
    categories = db.session.query(Product.category).distinct().filter(Product.category.isnot(None)).all()
    category_list = [c[0] for c in categories if c[0]]
    # Add default categories if none exist
    default_categories = ["Chasing ROV Units", "Chasing ROV Accessories", "Chasing ROV Spare Parts"]
    for default_cat in default_categories:
        if default_cat not in category_list:
            category_list.append(default_cat)
    return render_template('products/form.html', product=None, categories=category_list)

@bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        
        # Auto-generate SKU if not provided and product doesn't have one
        sku = request.form.get('sku') or None
        if not sku and not product.sku:
            name = request.form.get('name', '').strip()
            if name:
                sku_base = ''.join(c.upper() if c.isalnum() else '' for c in name)[:15]
                counter = 1
                sku = f"{sku_base}{counter:03d}"
                while Product.query.filter(Product.sku == sku, Product.id != product.id).first():
                    counter += 1
                    sku = f"{sku_base}{counter:03d}"
        
        product.sku = sku
        product.price = float(request.form.get('price'))
        product.tax_rate = float(request.form.get('tax_rate') or 0)
        product.category = request.form.get('category')
        product.is_active = request.form.get('is_active') == 'on'
        has_variants = request.form.get('has_variants') == 'on'
        product.has_variants = has_variants
        
        # Delete existing options and variants if disabling variations
        if not has_variants:
            # Delete in correct order: values first, then options, then variants
            options_to_delete = ProductOption.query.filter_by(product_id=product.id).all()
            for option in options_to_delete:
                ProductOptionValue.query.filter_by(option_id=option.id).delete()
            ProductOption.query.filter_by(product_id=product.id).delete()
            ProductVariant.query.filter_by(product_id=product.id).delete()
        else:
            # Handle variant updates (similar to create)
            # For simplicity, delete and recreate - delete in correct order
            options_to_delete = ProductOption.query.filter_by(product_id=product.id).all()
            for option in options_to_delete:
                ProductOptionValue.query.filter_by(option_id=option.id).delete()
            ProductOption.query.filter_by(product_id=product.id).delete()
            ProductVariant.query.filter_by(product_id=product.id).delete()
            
            option_names = request.form.getlist('option_name[]')
            option_values_list = request.form.getlist('option_values[]')
            
            options = []
            for idx, option_name in enumerate(option_names):
                if option_name.strip():
                    option = ProductOption(
                        product_id=product.id,
                        name=option_name.strip(),
                        display_order=idx
                    )
                    db.session.add(option)
                    db.session.flush()
                    
                    values_str = option_values_list[idx] if idx < len(option_values_list) else ''
                    values = [v.strip() for v in values_str.split(',') if v.strip()]
                    
                    for val_idx, value in enumerate(values):
                        option_value = ProductOptionValue(
                            option_id=option.id,
                            value=value,
                            display_order=val_idx
                        )
                        db.session.add(option_value)
                    
                    options.append(option)
            
            if options:
                all_value_combos = []
                for option in options:
                    values = [v.value for v in option.values]
                    all_value_combos.append(values)
                
                variant_combinations = list(itertools_product(*all_value_combos))
                base_price = float(request.form.get('price'))
                variant_prices = request.form.getlist('variant_price[]')
                variant_skus = request.form.getlist('variant_sku[]')
                
                for idx, combo in enumerate(variant_combinations):
                    variant_data = {}
                    for opt_idx, option in enumerate(options):
                        variant_data[option.name] = combo[opt_idx]
                    
                    variant_price = float(variant_prices[idx]) if idx < len(variant_prices) and variant_prices[idx] else base_price
                    variant_sku = variant_skus[idx] if idx < len(variant_skus) and variant_skus[idx] else None
                    
                    # Auto-generate variant SKU if not provided
                    if not variant_sku:
                        base_sku = product.sku or f"PROD{product.id:05d}"
                        variant_suffix = "-".join([str(v).upper()[:3] for v in combo])
                        variant_sku = f"{base_sku}-{variant_suffix}"
                        counter = 1
                        original_sku = variant_sku
                        while ProductVariant.query.filter(ProductVariant.sku == variant_sku).first():
                            variant_sku = f"{original_sku}-{counter}"
                            counter += 1
                    
                    variant = ProductVariant(
                        product_id=product.id,
                        sku=variant_sku,
                        price=variant_price,
                        tax_rate=float(request.form.get('tax_rate') or 0),
                        variant_data=json.dumps(variant_data),
                        is_active=True
                    )
                    db.session.add(variant)
        
        db.session.commit()
        return redirect(url_for('products.list_products'))
    
    # Get existing categories for dropdown suggestions
    categories = db.session.query(Product.category).distinct().filter(Product.category.isnot(None)).all()
    category_list = [c[0] for c in categories if c[0]]
    # Add default categories if none exist
    default_categories = ["Chasing ROV Units", "Chasing ROV Accessories", "Chasing ROV Spare Parts"]
    for default_cat in default_categories:
        if default_cat not in category_list:
            category_list.append(default_cat)
    return render_template('products/form.html', product=product, categories=category_list)

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

@bp.route('/<int:product_id>/details')
def get_product_details(product_id):
    """Get product details for slider panel"""
    product = Product.query.get_or_404(product_id)
    
    # Build product data
    product_data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'sku': product.sku,
        'price': product.price,
        'tax_rate': product.tax_rate,
        'category': product.category,
        'is_active': product.is_active,
        'has_variants': product.has_variants,
        'created_at': product.created_at.strftime('%B %d, %Y') if product.created_at else None,
        'variants': []
    }
    
    # Add variants if exists
    if product.has_variants and product.variants:
        for variant in product.variants:
            variant_data = {}
            if variant.variant_data:
                try:
                    variant_data = json.loads(variant.variant_data)
                except:
                    pass
            
            product_data['variants'].append({
                'id': variant.id,
                'sku': variant.sku,
                'price': variant.price,
                'tax_rate': variant.tax_rate or product.tax_rate,
                'variant_data': variant_data,
                'display_name': variant.get_variant_display_name(),
                'is_active': variant.is_active
            })
    
    # Add options if exists
    if product.options:
        product_data['options'] = []
        for option in product.options:
            product_data['options'].append({
                'name': option.name,
                'values': [v.value for v in option.values]
            })
    
    return jsonify(product_data)

@bp.route('/api/search')
def api_search_products():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:  # Minimum 2 characters
        return jsonify([])
    
    # Limit to 8 products to keep results manageable
    products = Product.query.filter(
        db.and_(
            Product.is_active == True,
            db.or_(
                Product.name.ilike(f'%{query}%'),
                Product.description.ilike(f'%{query}%'),
                Product.sku.ilike(f'%{query}%')
            )
        )
    ).limit(8).all()
    
    results = []
    max_results = 25  # Maximum total results to return
    
    for product in products:
        if len(results) >= max_results:
            break
            
        if product.has_variants and product.variants:
            # Return variants as separate results, but limit variants per product
            variant_count = 0
            max_variants_per_product = 5  # Limit variants per product
            for variant in product.variants:
                if variant.is_active and variant_count < max_variants_per_product and len(results) < max_results:
                    variant_dict = variant.to_dict()
                    variant_dict['name'] = f"{product.name} - {variant.get_variant_label()}"
                    variant_dict['product_name'] = product.name
                    results.append(variant_dict)
                    variant_count += 1
        else:
            results.append(product.to_dict())
    
    return jsonify(results)

@bp.route('/api/variants/<int:product_id>')
def api_get_variants(product_id):
    """Get all variants for a product"""
    product = Product.query.get_or_404(product_id)
    if not product.has_variants:
        return jsonify([])
    
    variants = [v.to_dict() for v in product.variants if v.is_active]
    return jsonify(variants)

