# Accounting ERP System

A comprehensive Accounting Enterprise Resource Planning (ERP) system built with Python, Streamlit, and MySQL/MariaDB. This application provides a complete double-entry bookkeeping solution with automated invoicing, dynamic reporting, and a user-friendly web interface.

## Features

- **Double-Entry Journal System**: Maintain accurate financial records with balanced debit and credit entries
- **Chart of Accounts**: Manage account types (Asset, Liability, Equity, Revenue, Expense) and individual accounts
- **Customer & Vendor Management**: Track clients and suppliers with contact information
- **Employee Management**: Maintain employee records with roles and departments
- **Product & Services Catalog**: Manage inventory items and pricing
- **Tax Management**: Configure tax rates and apply them to transactions
- **Payment Methods**: Define available payment options
- **Invoice Generation**: Create and manage customer invoices
- **Journal Entries**: Record manual accounting transactions
- **General Ledger**: View detailed transaction history
- **Financial Dashboard**: Real-time metrics for assets, liabilities, and equity
- **Trial Balance Reports**: Generate and download PDF reports of account balances

## Prerequisites

- Python 3.13 or higher
- MySQL or MariaDB server
- uv (fast Python package installer)

## Installation

1. **Install uv** (if not already installed):
   - On Linux/macOS:
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
   - On Windows:
     ```powershell
     powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```
     Or using winget:
     ```cmd
     winget install astral-sh.uv
     ```

2. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd accounting-erp
   ```

3. **Install dependencies and create virtual environment:**
   ```bash
   uv sync
   ```

   This will automatically create a virtual environment and install all required packages.

## Database Setup

1. **Start your MySQL/MariaDB server** and ensure it's running.

2. **Create the database and tables:**
   - Open your MySQL/MariaDB client (e.g., `mysql -u root -p`)
   - Run the SQL script:
     ```sql
     SOURCE accounting.sql;
     ```
   - Alternatively, you can run the script from the command line:
     ```bash
     mysql -u root -p < accounting.sql
     ```

3. **Configure database connection (optional):**
   - If your database credentials differ from the defaults, edit `database.py` and update the `mysql_url` variable:
     ```python
     mysql_url = "mysql+mysqlconnector://username:password@localhost:3306/accounting_erp"
     ```

## Running the Application

**Start the Streamlit app:**
```bash
uv run streamlit run app.py
```

**Access the application:**
- Open your web browser and go to `http://localhost:8501`
- The app will automatically initialize the database connection

## Usage Guide

### Dashboard
- View real-time financial metrics (Total Assets, Liabilities, Equity)
- See account balances in a table format
- Download Trial Balance PDF reports

### Chart of Accounts
- **Manage Account Types:** Add categories like Asset, Liability, Equity, Revenue, Expense
- **Add Accounts:** Create new accounts with names, codes, and assign types
- **View Balances:** See current account balances

### Employees
- Add employee records with name, role, department, and hire date
- View and manage employee information

### Customers
- Add customer details including name, email, and phone
- Manage client database

### Vendors
- Add vendor/supplier information with company name, contact, and tax ID
- Track business partners

### Products & Services
- Create product catalog with names, unit prices, and categories
- Manage inventory items

### Taxes
- Define tax rates and names (e.g., Sales Tax 8.5%)
- Apply taxes to transactions

### Payment Methods
- Configure payment options (Cash, Credit Card, Bank Transfer, etc.)

### Invoices
- Generate customer invoices
- Link invoices to customers and employees
- Track invoice status and totals

### Journal Entries
- Record manual accounting transactions
- Ensure double-entry balance (debits = credits)
- Link entries to employees, invoices, vendors, or payment methods

### General Ledger
- View detailed transaction history
- Filter and analyze journal entries

## Project Structure

```
accounting-erp/
├── accounting.sql          # Database schema and initial data
├── app.py                  # Main Streamlit application
├── database.py             # Database models and connection logic
├── main.py                 # Simple entry point (not used in production)
├── pyproject.toml          # Project configuration and dependencies
├── README.md               # This file
└── __pycache__/            # Python bytecode cache
```

## Technologies Used

- **Python 3.13+**: Core programming language
- **Streamlit**: Web application framework
- **SQLModel**: ORM for database operations (built on SQLAlchemy)
- **MySQL Connector/Python**: Database driver
- **FPDF**: PDF generation for reports
- **Pandas**: Data manipulation and analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues or questions, please open an issue on the GitHub repository.

