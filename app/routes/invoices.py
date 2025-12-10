from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_file
from app import db
from app.models import Invoice, InvoiceItem, Client
from app.utils.pdf import generate_invoice_pdf
from datetime import datetime, timedelta
import os

bp = Blueprint('invoices', __name__, url_prefix='/invoices')

@bp.route('/')
def list_invoices():
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'invoice_number')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate per_page to prevent abuse
    if per_page not in [5, 10, 25, 50, 100]:
        per_page = 10
    
    query = Invoice.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if search:
        if search_by == 'client_name':
            query = query.join(Client).filter(Client.name.ilike(f'%{search}%'))
        elif search_by == 'invoice_number':
            query = query.filter(Invoice.invoice_number.ilike(f'%{search}%'))
        elif search_by == 'invoice_id':
            try:
                query = query.filter(Invoice.id == int(search))
            except:
                pass
    
    invoices = query.order_by(Invoice.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('invoices/list.html', invoices=invoices, status_filter=status_filter, search=search, search_by=search_by, per_page=per_page)

@bp.route('/new', methods=['GET', 'POST'])
def create_invoice():
    clients = Client.query.all()
    
    if request.method == 'POST':
        # Generate invoice number
        last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
        invoice_number = f"INV-{(last_invoice.id if last_invoice else 0) + 1:05d}"
        
        invoice = Invoice(
            invoice_number=invoice_number,
            client_id=request.form.get('client_id'),
            issue_date=datetime.strptime(request.form.get('issue_date'), '%Y-%m-%d'),
            due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d') if request.form.get('due_date') else None,
            status='draft',
            notes=request.form.get('notes'),
            terms=request.form.get('terms')
        )
        
        db.session.add(invoice)
        db.session.flush()
        
        # Add items
        item_count = len(request.form.getlist('items[0][description]'))
        for i in range(item_count):
            item = InvoiceItem(
                invoice_id=invoice.id,
                description=request.form.get(f'items[{i}][description]'),
                quantity=float(request.form.get(f'items[{i}][quantity]') or 1),
                unit_price=float(request.form.get(f'items[{i}][unit_price]') or 0),
                tax_rate=float(request.form.get(f'items[{i}][tax_rate]') or 0)
            )
            db.session.add(item)
        
        db.session.commit()
        return redirect(url_for('invoices.view_invoice', invoice_id=invoice.id))
    
    return render_template('invoices/form.html', clients=clients, invoice=None, now=datetime.now())

@bp.route('/<int:invoice_id>')
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    subtotal = sum(item.subtotal for item in invoice.items)
    tax_total = sum(item.tax for item in invoice.items)
    return render_template('invoices/view.html', invoice=invoice, subtotal=subtotal, tax_total=tax_total)

@bp.route('/<int:invoice_id>/edit', methods=['GET', 'POST'])
def edit_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    clients = Client.query.all()
    
    if request.method == 'POST':
        invoice.client_id = request.form.get('client_id')
        invoice.issue_date = datetime.strptime(request.form.get('issue_date'), '%Y-%m-%d')
        invoice.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d') if request.form.get('due_date') else None
        invoice.status = request.form.get('status')
        invoice.notes = request.form.get('notes')
        invoice.terms = request.form.get('terms')
        
        # Clear existing items
        InvoiceItem.query.filter_by(invoice_id=invoice.id).delete()
        
        # Add new items
        item_count = len(request.form.getlist('items[0][description]'))
        for i in range(item_count):
            desc = request.form.get(f'items[{i}][description]')
            if desc:
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=desc,
                    quantity=float(request.form.get(f'items[{i}][quantity]') or 1),
                    unit_price=float(request.form.get(f'items[{i}][unit_price]') or 0),
                    tax_rate=float(request.form.get(f'items[{i}][tax_rate]') or 0)
                )
                db.session.add(item)
        
        db.session.commit()
        return redirect(url_for('invoices.view_invoice', invoice_id=invoice.id))
    
    return render_template('invoices/form.html', clients=clients, invoice=invoice, now=datetime.now())

@bp.route('/<int:invoice_id>/delete', methods=['POST'])
def delete_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    db.session.delete(invoice)
    db.session.commit()
    return redirect(url_for('invoices.list_invoices'))

@bp.route('/<int:invoice_id>/pdf')
def download_pdf(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    pdf_file = generate_invoice_pdf(invoice)
    
    if os.path.exists(pdf_file):
        return send_file(pdf_file, as_attachment=True, download_name=f"{invoice.invoice_number}.pdf")
    
    return "PDF generation failed", 500

@bp.route('/api/list')
def api_list_invoices():
    invoices = Invoice.query.all()
    return jsonify([invoice.to_dict() for invoice in invoices])
