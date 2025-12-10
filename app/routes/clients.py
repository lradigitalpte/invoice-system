from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app import db
from app.models import Client

bp = Blueprint('clients', __name__, url_prefix='/clients')

@bp.route('/')
def list_clients():
    search = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'name')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate per_page to prevent abuse
    if per_page not in [5, 10, 25, 50, 100]:
        per_page = 10
    
    query = Client.query
    
    if search:
        if search_by == 'name':
            query = query.filter(Client.name.ilike(f'%{search}%'))
        elif search_by == 'client_id':
            try:
                query = query.filter(Client.id == int(search))
            except:
                pass
        elif search_by == 'email':
            query = query.filter(Client.email.ilike(f'%{search}%'))
    
    clients = query.order_by(Client.name).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('clients/list.html', clients=clients, search=search, search_by=search_by, per_page=per_page)

@bp.route('/new', methods=['GET', 'POST'])
def create_client():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            return render_template('clients/form.html', client=None, error='Email is required.'), 400
        
        client = Client(
            name=request.form.get('name'),
            email=email,
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            zip_code=request.form.get('zip_code'),
            country=request.form.get('country'),
            tax_id=request.form.get('tax_id')
        )
        db.session.add(client)
        db.session.commit()
        return redirect(url_for('clients.list_clients'))
    return render_template('clients/form.html', client=None)

@bp.route('/<int:client_id>/edit', methods=['GET', 'POST'])
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            return render_template('clients/form.html', client=client, error='Email is required.'), 400
        
        client.name = request.form.get('name')
        client.email = email
        client.phone = request.form.get('phone')
        client.address = request.form.get('address')
        client.city = request.form.get('city')
        client.state = request.form.get('state')
        client.zip_code = request.form.get('zip_code')
        client.country = request.form.get('country')
        client.tax_id = request.form.get('tax_id')
        db.session.commit()
        return redirect(url_for('clients.list_clients'))
    return render_template('clients/form.html', client=client)

@bp.route('/<int:client_id>/delete', methods=['POST'])
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('clients.list_clients'))

@bp.route('/api/list')
def api_list_clients():
    clients = Client.query.all()
    return jsonify([client.to_dict() for client in clients])

@bp.route('/api/search')
def api_search_clients():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    clients = Client.query.filter(
        db.or_(
            Client.name.ilike(f'%{query}%'),
            Client.email.ilike(f'%{query}%'),
            Client.phone.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    return jsonify([client.to_dict() for client in clients])

