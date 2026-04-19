-- Create Database 
CREATE DATABASE IF NOT EXISTS accounting_erp; 
USE accounting_erp; 

-- Account Type Table
CREATE TABLE account_type (
    type_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL
);

-- Accounts Table 
CREATE TABLE account ( 
    account_id INT PRIMARY KEY, 
    account_name VARCHAR(100) NOT NULL, 
    account_code VARCHAR(50), 
    type_id INT,
    balance DECIMAL(15,2) DEFAULT 0.00,
    FOREIGN KEY (type_id) REFERENCES account_type(type_id)
); 

-- Customers Table 
CREATE TABLE customer ( 
    customer_id INT AUTO_INCREMENT PRIMARY KEY, 
    name VARCHAR(100) NOT NULL, 
    email VARCHAR(100), 
    phone VARCHAR(50)
); 

-- Employees Table
CREATE TABLE employee (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(100),
    department VARCHAR(100),
    hire_date DATE
);

-- Invoices Table
CREATE TABLE invoice (
    invoice_id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    total DECIMAL(15,2) DEFAULT 0.00,
    status VARCHAR(50),
    customer_id INT,
    employee_id INT,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
);

-- Vendors Table 
CREATE TABLE vendor ( 
    vendor_id INT AUTO_INCREMENT PRIMARY KEY, 
    company_name VARCHAR(100) NOT NULL, 
    contact VARCHAR(100), 
    tax_id VARCHAR(50)
); 

-- Payment Methods Table
CREATE TABLE payment_method (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    method_name VARCHAR(100) NOT NULL
);

-- Products Table
CREATE TABLE product (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    unit_price DECIMAL(15,2) DEFAULT 0.00,
    category VARCHAR(100)
);

-- Taxes Table
CREATE TABLE tax (
    tax_id INT AUTO_INCREMENT PRIMARY KEY,
    tax_name VARCHAR(100) NOT NULL,
    percentage DECIMAL(5,2) DEFAULT 0.00
);

-- Journal Entries Table 
CREATE TABLE journal_entry ( 
    entry_id INT AUTO_INCREMENT PRIMARY KEY, 
    date DATETIME DEFAULT CURRENT_TIMESTAMP, 
    description VARCHAR(255), 
    status VARCHAR(50),
    employee_id INT,
    invoice_id INT,
    vendor_id INT,
    payment_id INT,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id),
    FOREIGN KEY (invoice_id) REFERENCES invoice(invoice_id),
    FOREIGN KEY (vendor_id) REFERENCES vendor(vendor_id),
    FOREIGN KEY (payment_id) REFERENCES payment_method(payment_id)
); 

-- Journal Items Table (Ledger Lines)
CREATE TABLE journal_item ( 
    entry_id INT, 
    line_no INT, 
    debit DECIMAL(15,2) DEFAULT 0.00, 
    credit DECIMAL(15,2) DEFAULT 0.00, 
    account_id INT, 
    product_id INT,
    tax_id INT,
    PRIMARY KEY (entry_id, line_no),
    FOREIGN KEY (entry_id) REFERENCES journal_entry(entry_id), 
    FOREIGN KEY (account_id) REFERENCES account(account_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    FOREIGN KEY (tax_id) REFERENCES tax(tax_id)
); 

-- Insert default account types
INSERT INTO account_type (category_name) VALUES ('Asset'), ('Liability'), ('Equity'), ('Revenue'), ('Expense');
