from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from app import db
from app.models import CompanySettings
from werkzeug.utils import secure_filename
import os
from datetime import datetime

bp = Blueprint('settings', __name__, url_prefix='/settings')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'uploads', 'logos')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/company', methods=['GET', 'POST'])
def company_settings():
    settings = CompanySettings.get_settings()
    
    if request.method == 'POST':
        # Update company information
        settings.company_name = request.form.get('company_name', '')
        settings.company_address = request.form.get('company_address', '')
        settings.company_city = request.form.get('company_city', '')
        settings.company_state = request.form.get('company_state', '')
        settings.company_zip = request.form.get('company_zip', '')
        settings.company_country = request.form.get('company_country', '')
        settings.company_phone = request.form.get('company_phone', '')
        settings.company_email = request.form.get('company_email', '')
        settings.company_website = request.form.get('company_website', '')
        settings.company_tax_id = request.form.get('company_tax_id', '')
        
        # Update payment details
        settings.bank_name = request.form.get('bank_name', '')
        settings.bank_account_number = request.form.get('bank_account_number', '')
        settings.bank_routing_number = request.form.get('bank_routing_number', '')
        settings.bank_swift_code = request.form.get('bank_swift_code', '')
        settings.payment_instructions = request.form.get('payment_instructions', '')
        settings.payment_methods = request.form.get('payment_methods', '')
        
        # Handle logo upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename and allowed_file(file.filename):
                # Create upload directory if it doesn't exist
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                # Delete old logo if exists
                if settings.logo_path and os.path.exists(settings.logo_path):
                    try:
                        os.remove(settings.logo_path)
                    except:
                        pass
                
                # Save new logo
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                settings.logo_filename = filename
                settings.logo_path = filepath
        
        db.session.commit()
        flash('Company settings updated successfully!', 'success')
        return redirect(url_for('settings.company_settings'))
    
    return render_template('settings/company.html', settings=settings)

@bp.route('/logo/<filename>')
def serve_logo(filename):
    """Serve uploaded logo files"""
    return send_from_directory(UPLOAD_FOLDER, filename)

