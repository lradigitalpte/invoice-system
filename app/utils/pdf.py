from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, HRFlowable
from reportlab.lib import colors
from datetime import datetime
import os
from PIL import Image as PILImage

# Define custom colors
PRIMARY_COLOR = colors.HexColor('#3b82f6')
DARK_COLOR = colors.HexColor('#111827')
LIGHT_BG = colors.HexColor('#f9fafb')
BORDER_COLOR = colors.HexColor('#e5e7eb')
TEXT_COLOR = colors.HexColor('#374151')
SUCCESS_COLOR = colors.HexColor('#10b981')

def generate_invoice_pdf(invoice):
    """Generate a professional industry-standard PDF for an invoice"""
    from app.models import CompanySettings
    
    # Create data directory path relative to project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pdf_dir = os.path.join(base_dir, 'data', 'invoices')
    os.makedirs(pdf_dir, exist_ok=True)
    
    filename = os.path.join(pdf_dir, f"{invoice.invoice_number}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Define custom styles
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#9ca3af'),
        fontName='Helvetica',
        spaceAfter=2
    )
    
    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=11,
        textColor=DARK_COLOR,
        fontName='Helvetica-Bold',
        spaceAfter=6
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=DARK_COLOR,
        fontName='Helvetica-Bold',
        spaceAfter=8,
        spaceBefore=6
    )
    
    # Get company settings
    company = CompanySettings.get_settings()
    
    # HEADER: Company logo and INVOICE title
    logo_image = None
    if company.logo_path and os.path.exists(company.logo_path):
        try:
            img = PILImage.open(company.logo_path)
            max_height = 0.8 * inch
            ratio = max_height / img.height
            new_width = min(img.width * ratio, 1.8 * inch)
            logo_image = Image(company.logo_path, width=new_width, height=min(max_height, img.height * (new_width / img.width)))
        except:
            pass
    
    if logo_image:
        header_data = [[logo_image, Paragraph("<font size='24' color='#111827'><b>INVOICE</b></font>", styles['Normal'])]]
    else:
        header_data = [['', Paragraph("<font size='24' color='#111827'><b>INVOICE</b></font>", styles['Normal'])]]
    
    header_table = Table(header_data, colWidths=[1.8*inch, 4.7*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # COMPANY INFO (Left side)
    company_info = f"<b>{company.company_name or 'Your Company'}</b>"
    if company.company_address:
        company_info += f"<br/>{company.company_address}"
    if company.company_city or company.company_state:
        company_info += f"<br/>{company.company_city or ''} {company.company_state or ''} {company.company_zip or ''}"
    if company.company_phone:
        company_info += f"<br/>{company.company_phone}"
    if company.company_email:
        company_info += f"<br/>{company.company_email}"
    
    elements.append(Paragraph(company_info, label_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # THREE-COLUMN LAYOUT: Invoice Details | Bill To | (Empty)
    invoice_details_text = f"""<b style="font-size: 11px">Invoice Details</b><br/><br/>
    <b>Invoice #:</b> {invoice.invoice_number}<br/>
    <b>Date:</b> {invoice.issue_date.strftime('%b %d, %Y')}<br/>
    <b>Due Date:</b> {invoice.due_date.strftime('%b %d, %Y') if invoice.due_date else 'Not specified'}
    """
    
    client = invoice.client
    bill_to_text = f"""<b style="font-size: 11px">Bill To</b><br/><br/>
    <b>{client.name}</b><br/>
    {client.address or ''}<br/>
    {client.city or ''}{', ' + client.state if client.state else ''} {client.zip_code or ''}<br/>
    {client.country or ''}<br/>
    {f'Email: {client.email}' if client.email else ''}<br/>
    {f'Phone: {client.phone}' if client.phone else ''}
    """
    
    details_layout = Table(
        [[Paragraph(invoice_details_text, label_style), Paragraph(bill_to_text, label_style), '']],
        colWidths=[2.2*inch, 2.2*inch, 1.6*inch]
    )
    details_layout.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(details_layout)
    elements.append(Spacer(1, 0.2*inch))
    
    # ITEMS TABLE - Clean design with proper alignment
    items_data = [['Description', 'Qty', 'Unit Price', 'Tax %', 'Amount']]
    
    for item in invoice.items:
        items_data.append([
            Paragraph(item.description or '', value_style),
            Paragraph(f"{item.quantity:g}", value_style),
            Paragraph(f"${item.unit_price:.2f}", value_style),
            Paragraph(f"{item.tax_rate:.1f}%", value_style),
            Paragraph(f"${item.total:.2f}", value_style)
        ])
    
    items_table = Table(items_data, colWidths=[2.8*inch, 0.7*inch, 1.0*inch, 0.8*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        # Header row - blue background
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
        ('PADDING', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('PADDING', (0, 1), (-1, -1), 8),
        ('TEXTCOLOR', (0, 1), (-1, -1), DARK_COLOR),
        
        ('GRID', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # SUMMARY SECTION - Right-aligned, separated from items
    subtotal = sum(item.subtotal for item in invoice.items)
    tax_total = sum(item.tax for item in invoice.items)
    total_amount = invoice.get_total()
    
    summary_data = []
    summary_data.append([Paragraph('<b>Subtotal</b>', value_style), Paragraph(f'${subtotal:.2f}', value_style)])
    summary_data.append([Paragraph('<b>Tax</b>', value_style), Paragraph(f'${tax_total:.2f}', value_style)])
    summary_data.append([Paragraph('<b style="font-size: 12px">TOTAL</b>', value_style), Paragraph(f'<b style="font-size: 12px">${total_amount:.2f}</b>', value_style)])
    
    if invoice.get_paid_amount() > 0:
        summary_data.append([Paragraph('<b>Paid</b>', label_style), Paragraph(f'${invoice.get_paid_amount():.2f}', label_style)])
        balance = invoice.get_balance()
        summary_data.append([Paragraph('<b>Balance Due</b>', label_style), Paragraph(f'<font color="#ef4444"><b>${balance:.2f}</b></font>', label_style)])
    
    summary_table = Table(summary_data, colWidths=[1.3*inch, 1.3*inch])
    summary_table.setStyle(TableStyle([
        # Subtotal and Tax rows
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 1), 10),
        ('ALIGN', (0, 0), (0, 1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, 1), 'RIGHT'),
        ('TEXTCOLOR', (0, 0), (-1, 1), DARK_COLOR),
        ('PADDING', (0, 0), (-1, 1), 8),
        ('BACKGROUND', (0, 0), (-1, 1), LIGHT_BG),
        
        # TOTAL row
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 2), (-1, 2), 11),
        ('ALIGN', (0, 2), (0, 2), 'RIGHT'),
        ('ALIGN', (1, 2), (1, 2), 'RIGHT'),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.white),
        ('BACKGROUND', (0, 2), (-1, 2), PRIMARY_COLOR),
        ('PADDING', (0, 2), (-1, 2), 10),
        
        # Optional paid/balance rows
        ('FONTNAME', (0, 3), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 3), (-1, -1), 9),
        ('ALIGN', (0, 3), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 3), (1, -1), 'RIGHT'),
        ('TEXTCOLOR', (0, 3), (-1, -1), DARK_COLOR),
        ('PADDING', (0, 3), (-1, -1), 6),
        ('BACKGROUND', (0, 3), (-1, -1), LIGHT_BG),
        
        ('GRID', (0, 0), (-1, -1), 1, BORDER_COLOR),
    ]))
    
    # Right-align the summary table using a wrapper
    summary_wrapper = Table([['', summary_table]], colWidths=[4.5*inch, 2.6*inch])
    summary_wrapper.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (1, 0), (1, 0), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(summary_wrapper)
    elements.append(Spacer(1, 0.3*inch))
    
    # NOTES, TERMS, PAYMENT INFO
    if invoice.notes:
        elements.append(Paragraph('<b>Notes</b>', section_style))
        elements.append(Paragraph(invoice.notes, label_style))
        elements.append(Spacer(1, 0.1*inch))
    
    if invoice.terms:
        elements.append(Paragraph('<b>Terms & Conditions</b>', section_style))
        elements.append(Paragraph(invoice.terms, label_style))
        elements.append(Spacer(1, 0.1*inch))
    
    # Payment Details - Always show if any bank info exists
    payment_details = []
    if company.bank_name:
        payment_details.append(f"<b>Bank:</b> {company.bank_name}")
    if company.bank_account_number:
        payment_details.append(f"<b>Account Number:</b> {company.bank_account_number}")
    if company.bank_routing_number:
        payment_details.append(f"<b>Routing Number:</b> {company.bank_routing_number}")
    if company.bank_swift_code:
        payment_details.append(f"<b>SWIFT Code:</b> {company.bank_swift_code}")
    if company.payment_methods:
        payment_details.append(f"<b>Payment Methods:</b> {company.payment_methods}")
    if company.payment_instructions:
        payment_details.append(f"<br/>{company.payment_instructions}")
    
    if payment_details:
        elements.append(Paragraph('<b>Payment Instructions</b>', section_style))
        elements.append(Paragraph('<br/>'.join(payment_details), label_style))
    
    # FOOTER
    elements.append(Spacer(1, 0.2*inch))
    footer_text = f"Thank you for your business! | Invoice #: {invoice.invoice_number} | Generated: {datetime.now().strftime('%B %d, %Y')}"
    elements.append(Paragraph(f"<i><font size='8' color='#9ca3af'>{footer_text}</font></i>", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    return filename


def generate_quotation_pdf(quotation):
    """Generate a professional industry-standard PDF for a quotation"""
    from app.models import CompanySettings
    
    # Create data directory path relative to project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pdf_dir = os.path.join(base_dir, 'data', 'quotations')
    os.makedirs(pdf_dir, exist_ok=True)
    
    filename = os.path.join(pdf_dir, f"{quotation.quotation_number}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Define custom styles
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#9ca3af'),
        fontName='Helvetica',
        spaceAfter=2
    )
    
    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=11,
        textColor=DARK_COLOR,
        fontName='Helvetica-Bold',
        spaceAfter=6
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=DARK_COLOR,
        fontName='Helvetica-Bold',
        spaceAfter=8,
        spaceBefore=6
    )
    
    # Get company settings
    company = CompanySettings.get_settings()
    
    # HEADER: Company logo and QUOTATION title
    logo_image = None
    if company.logo_path and os.path.exists(company.logo_path):
        try:
            img = PILImage.open(company.logo_path)
            max_height = 0.8 * inch
            ratio = max_height / img.height
            new_width = min(img.width * ratio, 1.8 * inch)
            logo_image = Image(company.logo_path, width=new_width, height=min(max_height, img.height * (new_width / img.width)))
        except:
            pass
    
    if logo_image:
        header_data = [[logo_image, Paragraph("<font size='24' color='#111827'><b>QUOTATION</b></font>", styles['Normal'])]]
    else:
        header_data = [['', Paragraph("<font size='24' color='#111827'><b>QUOTATION</b></font>", styles['Normal'])]]
    
    header_table = Table(header_data, colWidths=[1.8*inch, 4.7*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # COMPANY INFO (Left side)
    company_info = f"<b>{company.company_name or 'Your Company'}</b>"
    if company.company_address:
        company_info += f"<br/>{company.company_address}"
    if company.company_city or company.company_state:
        company_info += f"<br/>{company.company_city or ''} {company.company_state or ''} {company.company_zip or ''}"
    if company.company_phone:
        company_info += f"<br/>{company.company_phone}"
    if company.company_email:
        company_info += f"<br/>{company.company_email}"
    
    elements.append(Paragraph(company_info, label_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # THREE-COLUMN LAYOUT: Quotation Details | Prepared For | (Empty)
    quotation_details_text = f"""<b style="font-size: 11px">Quotation Details</b><br/><br/>
    <b>Quotation #:</b> {quotation.quotation_number}<br/>
    <b>Date:</b> {quotation.issue_date.strftime('%b %d, %Y')}<br/>
    <b>Valid Until:</b> {quotation.valid_until.strftime('%b %d, %Y') if quotation.valid_until else 'Not specified'}
    """
    
    client = quotation.client
    prepared_for_text = f"""<b style="font-size: 11px">Prepared For</b><br/><br/>
    <b>{client.name}</b><br/>
    {client.address or ''}<br/>
    {client.city or ''}{', ' + client.state if client.state else ''} {client.zip_code or ''}<br/>
    {client.country or ''}<br/>
    {f'Email: {client.email}' if client.email else ''}<br/>
    {f'Phone: {client.phone}' if client.phone else ''}
    """
    
    details_layout = Table(
        [[Paragraph(quotation_details_text, label_style), Paragraph(prepared_for_text, label_style), '']],
        colWidths=[2.2*inch, 2.2*inch, 1.6*inch]
    )
    details_layout.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(details_layout)
    elements.append(Spacer(1, 0.2*inch))
    
    # ITEMS TABLE - Clean design with proper alignment
    items_data = [['Description', 'Qty', 'Unit Price', 'Tax %', 'Amount']]
    
    for item in quotation.items:
            items_data.append([
                Paragraph(item.description or '', value_style),
                Paragraph(f"{item.quantity:g}", value_style),
                Paragraph(f"${item.unit_price:.2f}", value_style),
                Paragraph(f"{item.tax_rate:.1f}%", value_style),
                Paragraph(f"${item.total:.2f}", value_style)
            ])
    
    items_table = Table(items_data, colWidths=[2.8*inch, 0.7*inch, 1.0*inch, 0.8*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        # Header row - blue background
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
        ('PADDING', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('PADDING', (0, 1), (-1, -1), 8),
        ('TEXTCOLOR', (0, 1), (-1, -1), DARK_COLOR),
        
        ('GRID', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # SUMMARY SECTION - Right-aligned, separated from items
    subtotal = sum(item.subtotal for item in quotation.items)
    tax_total = sum(item.tax for item in quotation.items)
    total_amount = quotation.get_total()
    
    summary_data = []
    summary_data.append([Paragraph('<b>Subtotal</b>', value_style), Paragraph(f'', value_style)])
    summary_data.append([Paragraph('<b>Tax</b>', value_style), Paragraph(f'', value_style)])
    summary_data.append([Paragraph('<b style="font-size: 12px">TOTAL</b>', value_style), Paragraph(f'<b style="font-size: 12px"></b>', value_style)])
    
    summary_table = Table(summary_data, colWidths=[1.3*inch, 1.3*inch])
    summary_table.setStyle(TableStyle([
        # Subtotal and Tax rows
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 1), 10),
        ('ALIGN', (0, 0), (0, 1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, 1), 'RIGHT'),
        ('TEXTCOLOR', (0, 0), (-1, 1), DARK_COLOR),
        ('PADDING', (0, 0), (-1, 1), 8),
        ('BACKGROUND', (0, 0), (-1, 1), LIGHT_BG),
        
        # TOTAL row
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 2), (-1, 2), 11),
        ('ALIGN', (0, 2), (0, 2), 'RIGHT'),
        ('ALIGN', (1, 2), (1, 2), 'RIGHT'),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.white),
        ('BACKGROUND', (0, 2), (-1, 2), PRIMARY_COLOR),
        ('PADDING', (0, 2), (-1, 2), 10),
        
        ('GRID', (0, 0), (-1, -1), 1, BORDER_COLOR),
    ]))
    
    # Right-align the summary table using a wrapper
    summary_wrapper = Table([['', summary_table]], colWidths=[4.5*inch, 2.6*inch])
    summary_wrapper.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (1, 0), (1, 0), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(summary_wrapper)
    elements.append(Spacer(1, 0.3*inch))
    
    # NOTES AND TERMS
    if quotation.notes or quotation.terms:
        if quotation.notes:
            elements.append(Paragraph('<b>Notes</b>', section_style))
            elements.append(Paragraph(quotation.notes, label_style))
            elements.append(Spacer(1, 0.1*inch))
        
        if quotation.terms:
            elements.append(Paragraph('<b>Terms & Conditions</b>', section_style))
            elements.append(Paragraph(quotation.terms, label_style))
    
    # FOOTER
    elements.append(Spacer(1, 0.2*inch))
    footer_text = f"Thank you for your interest! | Quotation #: {quotation.quotation_number} | Generated: {datetime.now().strftime('%B %d, %Y')}"
    elements.append(Paragraph(f"<i><font size='8' color='#9ca3af'>{footer_text}</font></i>", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    return filename
