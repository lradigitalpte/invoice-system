# Invoicing System - Copilot Instructions

## Project Overview
This is an offline invoicing system built with Flask and SQLite. It allows companies to:
- Manage clients and company information
- Create and generate invoices
- Track payments and invoice status
- Export invoices as PDF
- View invoice history and reports

## Project Structure
- `app/` - Main Flask application
  - `models/` - Database models (Client, Invoice, InvoiceItem, Payment)
  - `routes/` - Flask blueprints for different features
  - `templates/` - HTML templates
  - `static/` - CSS and JavaScript files
  - `utils/` - Helper functions (PDF generation, database operations)
- `data/` - SQLite database and file storage
- `.vscode/` - VS Code configuration

## Key Features to Implement
1. Client Management (CRUD operations)
2. Invoice Generation with customizable templates
3. Payment Tracking
4. PDF Export functionality
5. Invoice History and Reports
6. Offline-first data storage with SQLite

## Setup Instructions
1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python run.py`
3. Access via browser: `http://localhost:5000`

## Development Guidelines
- Use SQLAlchemy ORM for database operations
- Keep database queries efficient
- Ensure all file exports are stored in `data/` directory
- Test PDF generation thoroughly
