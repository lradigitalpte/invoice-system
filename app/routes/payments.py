from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app import db
from app.models import Payment, Invoice
from datetime import datetime

bp = Blueprint('payments', __name__, url_prefix='/payments')

@bp.route('/<int:invoice_id>/add', methods=['GET', 'POST'])
def add_payment(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    
    if request.method == 'POST':
        payment = Payment(
            invoice_id=invoice_id,
            amount=float(request.form.get('amount')),
            payment_date=datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d'),
            payment_method=request.form.get('payment_method'),
            notes=request.form.get('notes')
        )
        db.session.add(payment)
        
        # Update invoice status if fully paid
        if payment.amount >= invoice.get_balance():
            invoice.status = 'paid'
        elif invoice.status != 'overdue':
            invoice.status = 'sent'
        
        db.session.commit()
        return redirect(url_for('invoices.view_invoice', invoice_id=invoice_id))
    
    return render_template('payments/add.html', invoice=invoice, now=datetime.now())

@bp.route('/<int:payment_id>/delete', methods=['POST'])
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    invoice_id = payment.invoice_id
    invoice = payment.invoice
    
    db.session.delete(payment)
    
    # Reset invoice status
    if invoice.get_balance() > 0:
        invoice.status = 'sent'
    else:
        invoice.status = 'paid'
    
    db.session.commit()
    return redirect(url_for('invoices.view_invoice', invoice_id=invoice_id))

@bp.route('/api/list/<int:invoice_id>')
def api_list_payments(invoice_id):
    payments = Payment.query.filter_by(invoice_id=invoice_id).all()
    return jsonify([payment.to_dict() for payment in payments])
