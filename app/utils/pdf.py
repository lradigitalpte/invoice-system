from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from datetime import datetime
import os
from PIL import Image as PILImage

def generate_invoice_pdf(invoice):
    """Generate a PDF for an invoice"""
    from app.models import CompanySettings
    
    # Create data directory path relative to project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pdf_dir = os.path.join(base_dir, 'data', 'invoices')
    os.makedirs(pdf_dir, exist_ok=True)
    
    filename = os.path.join(pdf_dir, f"{invoice.invoice_number}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Get company settings
    company = CompanySettings.get_settings()
    
    # Company header with logo
    from reportlab.platypus import Table as PDFTable
    
    # Build company info
    company_info = f"""
    <b><font size="18">{company.company_name or 'Your Company Name'}</font></b><br/>
    """
    if company.company_address:
        company_info += f"{company.company_address}<br/>"
    if company.company_city or company.company_state or company.company_zip:
        city_state = f"{company.company_city or ''}, {company.company_state or ''} {company.company_zip or ''}".strip(', ')
        company_info += f"{city_state}<br/>"
    if company.company_country:
        company_info += f"{company.company_country}<br/>"
    if company.company_phone:
        company_info += f"Phone: {company.company_phone}<br/>"
    if company.company_email:
        company_info += f"Email: {company.company_email}<br/>"
    if company.company_website:
        company_info += f"Website: {company.company_website}<br/>"
    
    # Create header table with logo and company info
    header_cells = []
    
    # Left cell: Logo (if exists)
    logo_cell = ''
    if company.logo_path and os.path.exists(company.logo_path):
        try:
            # Resize logo to max 1.5 inches height
            img = PILImage.open(company.logo_path)
            max_height = 1.5 * inch
            ratio = max_height / img.height
            new_width = min(img.width * ratio, 2 * inch)  # Max width 2 inches
            logo_img = Image(company.logo_path, width=new_width, height=min(max_height, img.height * (new_width / img.width)))
            logo_cell = logo_img
        except Exception as e:
            logo_cell = ''
    else:
        logo_cell = ''
    
    # Right cell: Company info and INVOICE title
    right_content = [Paragraph(company_info, styles['Normal']), Spacer(1, 0.1*inch), Paragraph("<b><font size='24'>INVOICE</font></b>", styles['Normal'])]
    right_cell = right_content
    
    header_data = [[logo_cell, right_cell]]
    
    header_table = PDFTable(header_data, colWidths=[2.5*inch, 4*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
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
            Paragraph(item.description, styles['Normal']),
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
        elements.append(Spacer(1, 0.2*inch))
    
    # Payment details section
    if company.bank_name or company.bank_account_number or company.payment_instructions or company.payment_methods:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("<b>Payment Details:</b>", styles['Heading3']))
        
        payment_info = ""
        if company.bank_name:
            payment_info += f"<b>Bank:</b> {company.bank_name}<br/>"
        if company.bank_account_number:
            payment_info += f"<b>Account Number:</b> {company.bank_account_number}<br/>"
        if company.bank_routing_number:
            payment_info += f"<b>Routing Number:</b> {company.bank_routing_number}<br/>"
        if company.bank_swift_code:
            payment_info += f"<b>SWIFT Code:</b> {company.bank_swift_code}<br/>"
        if company.payment_methods:
            payment_info += f"<b>Payment Methods:</b> {company.payment_methods}<br/>"
        if company.payment_instructions:
            payment_info += f"<br/>{company.payment_instructions}<br/>"
        
        if payment_info:
            elements.append(Paragraph(payment_info, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    return filename


def generate_quotation_pdf(quotation):
    """Generate a PDF for a quotation"""
    # Create data directory path relative to project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pdf_dir = os.path.join(base_dir, 'data', 'quotations')
    os.makedirs(pdf_dir, exist_ok=True)
    
    filename = os.path.join(pdf_dir, f"{quotation.quotation_number}.pdf")
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
    elements.append(Paragraph("QUOTATION", company_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Quotation details
    quotation_info = f"""
    <b>Quotation #:</b> {quotation.quotation_number}<br/>
    <b>Date:</b> {quotation.issue_date.strftime('%B %d, %Y')}<br/>
    <b>Valid Until:</b> {quotation.valid_until.strftime('%B %d, %Y') if quotation.valid_until else 'Not specified'}<br/>
    <b>Status:</b> {quotation.status.upper()}
    """
    elements.append(Paragraph(quotation_info, styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Client information
    client = quotation.client
    client_info = f"""
    <b>Prepared For:</b><br/>
    {client.name}<br/>
    {client.address or ''}<br/>
    {client.city or ''}, {client.state or ''} {client.zip_code or ''}<br/>
    {client.country or ''}<br/>
    Email: {client.email or 'N/A'}<br/>
    Phone: {client.phone or 'N/A'}
    """
    elements.append(Paragraph(client_info, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Quotation items table
    data = [['Description', 'Qty', 'Unit Price', 'Tax %', 'Amount']]
    for item in quotation.items:
        data.append([
            item.description,
            f"{item.quantity}",
            f"${item.unit_price:.2f}",
            f"{item.tax_rate:.1f}%",
            f"${item.total:.2f}"
        ])
    
    # Totals row
    data.append(['', '', '', 'Subtotal:', f"${sum(item.subtotal for item in quotation.items):.2f}"])
    data.append(['', '', '', 'Tax:', f"${sum(item.tax for item in quotation.items):.2f}"])
    data.append(['', '', '', 'TOTAL:', f"${quotation.get_total():.2f}"])
    
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
    if quotation.notes or quotation.terms:
        elements.append(Paragraph("<b>Notes & Terms:</b>", styles['Heading3']))
        if quotation.notes:
            elements.append(Paragraph(quotation.notes, styles['Normal']))
        if quotation.terms:
            elements.append(Paragraph(quotation.terms, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    return filename

