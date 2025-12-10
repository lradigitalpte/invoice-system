from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_file
from app import db
from app.models import Quotation, QuotationItem, Client, Invoice, InvoiceItem
from app.utils.pdf import generate_quotation_pdf
from datetime import datetime, timedelta
import os

bp = Blueprint('quotations', __name__, url_prefix='/quotations')

@bp.route('/')
def list_quotations():
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '').strip()
    search_by = request.args.get('search_by', 'quotation_number')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate per_page to prevent abuse
    if per_page not in [5, 10, 25, 50, 100]:
        per_page = 10
    
    query = Quotation.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if search:
        if search_by == 'client_name':
            query = query.join(Client).filter(Client.name.ilike(f'%{search}%'))
        elif search_by == 'quotation_number':
            query = query.filter(Quotation.quotation_number.ilike(f'%{search}%'))
        elif search_by == 'quotation_id':
            try:
                query = query.filter(Quotation.id == int(search))
            except:
                pass
    
    quotations = query.order_by(Quotation.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('quotations/list.html', quotations=quotations, status_filter=status_filter, search=search, search_by=search_by, per_page=per_page)

@bp.route('/new', methods=['GET', 'POST'])
def create_quotation():
    clients = Client.query.all()
    
    if request.method == 'POST':
        # Generate quotation number
        last_quotation = Quotation.query.order_by(Quotation.id.desc()).first()
        quotation_number = f"QT-{(last_quotation.id if last_quotation else 0) + 1:05d}"
        
        quotation = Quotation(
            quotation_number=quotation_number,
            client_id=request.form.get('client_id'),
            issue_date=datetime.strptime(request.form.get('issue_date'), '%Y-%m-%d'),
            valid_until=datetime.strptime(request.form.get('valid_until'), '%Y-%m-%d') if request.form.get('valid_until') else None,
            status='pending',
            notes=request.form.get('notes'),
            terms=request.form.get('terms')
        )
        
        db.session.add(quotation)
        db.session.flush()
        
        # Add items
        item_count = len(request.form.getlist('items[0][description]'))
        for i in range(item_count):
            item = QuotationItem(
                quotation_id=quotation.id,
                description=request.form.get(f'items[{i}][description]'),
                quantity=float(request.form.get(f'items[{i}][quantity]') or 1),
                unit_price=float(request.form.get(f'items[{i}][unit_price]') or 0),
                tax_rate=float(request.form.get(f'items[{i}][tax_rate]') or 0)
            )
            db.session.add(item)
        
        db.session.commit()
        return redirect(url_for('quotations.view_quotation', quotation_id=quotation.id))
    
    return render_template('quotations/form.html', clients=clients, quotation=None, now=datetime.now())

@bp.route('/<int:quotation_id>')
def view_quotation(quotation_id):
    quotation = Quotation.query.get_or_404(quotation_id)
    subtotal = sum(item.subtotal for item in quotation.items)
    tax_total = sum(item.tax for item in quotation.items)
    return render_template('quotations/view.html', quotation=quotation, subtotal=subtotal, tax_total=tax_total)

@bp.route('/<int:quotation_id>/edit', methods=['GET', 'POST'])
def edit_quotation(quotation_id):
    quotation = Quotation.query.get_or_404(quotation_id)
    clients = Client.query.all()
    
    if request.method == 'POST':
        quotation.client_id = request.form.get('client_id')
        quotation.issue_date = datetime.strptime(request.form.get('issue_date'), '%Y-%m-%d')
        quotation.valid_until = datetime.strptime(request.form.get('valid_until'), '%Y-%m-%d') if request.form.get('valid_until') else None
        quotation.status = request.form.get('status')
        quotation.notes = request.form.get('notes')
        quotation.terms = request.form.get('terms')
        
        # Clear existing items
        QuotationItem.query.filter_by(quotation_id=quotation.id).delete()
        
        # Add new items
        item_count = len(request.form.getlist('items[0][description]'))
        for i in range(item_count):
            desc = request.form.get(f'items[{i}][description]')
            if desc:
                item = QuotationItem(
                    quotation_id=quotation.id,
                    description=desc,
                    quantity=float(request.form.get(f'items[{i}][quantity]') or 1),
                    unit_price=float(request.form.get(f'items[{i}][unit_price]') or 0),
                    tax_rate=float(request.form.get(f'items[{i}][tax_rate]') or 0)
                )
                db.session.add(item)
        
        db.session.commit()
        return redirect(url_for('quotations.view_quotation', quotation_id=quotation.id))
    
    return render_template('quotations/form.html', clients=clients, quotation=quotation, now=datetime.now())

@bp.route('/<int:quotation_id>/convert-to-invoice', methods=['POST'])
def convert_to_invoice(quotation_id):
    quotation = Quotation.query.get_or_404(quotation_id)
    
    # Generate invoice number
    last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
    invoice_number = f"INV-{(last_invoice.id if last_invoice else 0) + 1:05d}"
    
    # Create invoice from quotation
    invoice = Invoice(
        invoice_number=invoice_number,
        client_id=quotation.client_id,
        issue_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=30),
        status='draft',
        notes=quotation.notes,
        terms=quotation.terms
    )
    
    db.session.add(invoice)
    db.session.flush()
    
    # Copy items from quotation to invoice
    for q_item in quotation.items:
        invoice_item = InvoiceItem(
            invoice_id=invoice.id,
            description=q_item.description,
            quantity=q_item.quantity,
            unit_price=q_item.unit_price,
            tax_rate=q_item.tax_rate
        )
        db.session.add(invoice_item)
    
    # Update quotation status
    quotation.status = 'accepted'
    
    db.session.commit()
    return redirect(url_for('invoices.view_invoice', invoice_id=invoice.id))

@bp.route('/<int:quotation_id>/delete', methods=['POST'])
def delete_quotation(quotation_id):
    quotation = Quotation.query.get_or_404(quotation_id)
    db.session.delete(quotation)
    db.session.commit()
    return redirect(url_for('quotations.list_quotations'))

@bp.route('/<int:quotation_id>/pdf')
def download_pdf(quotation_id):
    quotation = Quotation.query.get_or_404(quotation_id)
    pdf_file = generate_quotation_pdf(quotation)
    
    if os.path.exists(pdf_file):
        return send_file(pdf_file, as_attachment=True, download_name=f"{quotation.quotation_number}.pdf")
    
    return "PDF generation failed", 500

@bp.route('/api/list')
def api_list_quotations():
    quotations = Quotation.query.all()
    return jsonify([quotation.to_dict() for quotation in quotations])
