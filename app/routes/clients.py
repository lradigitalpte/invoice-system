from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app import db
from app.models import Client

bp = Blueprint('clients', __name__, url_prefix='/clients')

@bp.route('/')
def list_clients():
    page = request.args.get('page', 1, type=int)
    clients = Client.query.paginate(page=page, per_page=20)
    return render_template('clients/list.html', clients=clients)

@bp.route('/new', methods=['GET', 'POST'])
def create_client():
    if request.method == 'POST':
        client = Client(
            name=request.form.get('name'),
            email=request.form.get('email'),
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
        client.name = request.form.get('name')
        client.email = request.form.get('email')
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
