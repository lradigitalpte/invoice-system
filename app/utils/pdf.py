from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from datetime import datetime
import os

def generate_invoice_pdf(invoice):
    """Generate a PDF for an invoice"""
    # Create data directory path relative to project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pdf_dir = os.path.join(base_dir, 'data', 'invoices')
    os.makedirs(pdf_dir, exist_ok=True)
    
    filename = os.path.join(pdf_dir, f"{invoice.invoice_number}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Company header
    company_style = ParagraphStyle(
        'CompanyHeader',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=6
    )
    elements.append(Paragraph("INVOICE", company_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Invoice details
    invoice_info = f"""
    <b>Invoice #:</b> {invoice.invoice_number}<br/>
    <b>Date:</b> {invoice.issue_date.strftime('%B %d, %Y')}<br/>
    <b>Due Date:</b> {invoice.due_date.strftime('%B %d, %Y') if invoice.due_date else 'Not specified'}<br/>
    <b>Status:</b> {invoice.status.upper()}
    """
    elements.append(Paragraph(invoice_info, styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Client information
    client = invoice.client
    client_info = f"""
    <b>Bill To:</b><br/>
    {client.name}<br/>
    {client.address or ''}<br/>
    {client.city or ''}, {client.state or ''} {client.zip_code or ''}<br/>
    {client.country or ''}<br/>
    Email: {client.email or 'N/A'}<br/>
    Phone: {client.phone or 'N/A'}
    """
    elements.append(Paragraph(client_info, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Invoice items table
    data = [['Description', 'Qty', 'Unit Price', 'Tax %', 'Amount']]
    for item in invoice.items:
        data.append([
            item.description,
            f"{item.quantity}",
            f"${item.unit_price:.2f}",
            f"{item.tax_rate:.1f}%",
            f"${item.total:.2f}"
        ])
    
    # Totals row
    data.append(['', '', '', 'Subtotal:', f"${sum(item.subtotal for item in invoice.items):.2f}"])
    data.append(['', '', '', 'Tax:', f"${sum(item.tax for item in invoice.items):.2f}"])
    data.append(['', '', '', 'TOTAL:', f"${invoice.get_total():.2f}"])
    
    if invoice.get_paid_amount() > 0:
        data.append(['', '', '', 'Paid:', f"${invoice.get_paid_amount():.2f}"])
        data.append(['', '', '', 'Balance:', f"${invoice.get_balance():.2f}"])
    
    table = Table(data, colWidths=[2.5*inch, 0.8*inch, 1*inch, 0.8*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (3, -3), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Notes and terms
    if invoice.notes or invoice.terms:
        elements.append(Paragraph("<b>Notes & Terms:</b>", styles['Heading3']))
        if invoice.notes:
            elements.append(Paragraph(invoice.notes, styles['Normal']))
        if invoice.terms:
            elements.append(Paragraph(invoice.terms, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    return filename
