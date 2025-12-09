# Offline Invoicing System

A simple, offline-first invoicing system built with Flask and SQLite for small businesses and freelancers.

## Features

- **Client Management**: Add, edit, and manage client information
- **Invoice Generation**: Create invoices with multiple line items
- **Payment Tracking**: Record payments and track invoice status
- **PDF Export**: Export invoices as professional PDF documents
- **Offline-First**: All data stored locally with SQLite
- **Simple Web Interface**: Easy-to-use web dashboard

## Requirements

- Python 3.7+
- Flask 2.3.3
- SQLAlchemy 2.0.21
- ReportLab 4.0.7

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python run.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

### Managing Clients
1. Navigate to the "Clients" section
2. Click "+ New Client" to add a client
3. Enter client details (name, email, phone, address, etc.)
4. Click "Save"

### Creating Invoices
1. Go to "Invoices" section
2. Click "+ New Invoice"
3. Select a client
4. Set invoice dates
5. Add line items with description, quantity, unit price, and tax rate
6. Add notes and payment terms if needed
7. Save the invoice

### Recording Payments
1. Open an invoice
2. Click "Add Payment"
3. Enter payment amount, date, and method
4. The invoice status will automatically update

### Exporting to PDF
1. Open an invoice
2. Click "Download PDF"
3. The PDF will be generated and downloaded

## Project Structure

```
├── app/
│   ├── models/          # Database models
│   ├── routes/          # Flask blueprints
│   ├── static/          # CSS and JavaScript
│   ├── templates/       # HTML templates
│   ├── utils/           # Helper functions
│   └── __init__.py      # Flask app initialization
├── data/                # SQLite database and generated files
├── run.py              # Application entry point
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Database Models

### Client
Stores client information including name, email, phone, address, and tax ID.

### Invoice
Represents an invoice with invoice number, client reference, dates, status, notes, and terms.

### InvoiceItem
Individual line items on an invoice with description, quantity, unit price, and tax rate.

### Payment
Records payments made on invoices with amount, date, and payment method.

## API Endpoints

- `GET /clients/api/list` - Get all clients
- `GET /invoices/api/list` - Get all invoices
- `GET /payments/api/list/<invoice_id>` - Get payments for an invoice

## Data Storage

All data is stored locally in SQLite database at `data/invoicing.db`. Generated PDFs are saved in `data/invoices/`.

## Notes

- This is designed for offline use. No internet connection is required
- Data is stored locally and is not synced to any cloud service
- Regular backups of the `data/` directory are recommended
- The application is single-user and should be run locally

## Future Enhancements

- Multi-user support with authentication
- Recurring invoices
- Invoice templates
- Multi-currency support
- Email invoice delivery
- Invoice reminders
- Advanced reporting and analytics
- Import/export functionality

## License

This project is open source and available for personal and commercial use.

## Support

For issues or questions, please refer to the documentation or contact support.
