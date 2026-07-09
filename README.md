# Accounting ERP System

A comprehensive Accounting Enterprise Resource Planning (ERP) system built with Python, Streamlit, and MySQL/MariaDB. This application provides a complete double-entry bookkeeping solution with automated invoicing, dynamic reporting, and a user-friendly web interface.

---

## Badges

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge\&logo=streamlit\&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge\&logo=mysql\&logoColor=white)
![SQLModel](https://img.shields.io/badge/SQLModel-ORM-success?style=for-the-badge)
![ERP](https://img.shields.io/badge/Project-Accounting%20ERP-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge)

---

## Table of Contents

* [Project Overview](#project-overview)
* [Features](#features)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Database Setup](#database-setup)
* [Running the Application](#running-the-application)
* [Usage Guide](#usage-guide)
* [Screenshots](#screenshots)
* [Technologies Used](#technologies-used)
* [Contributing](#contributing)
* [License](#license)
* [Support](#support)
* [Created By](#created-by)

---

# Project Overview

Managing financial records manually can be time-consuming and prone to errors. An Accounting ERP system simplifies this process by organizing financial data, automating transactions, and generating accurate reports.

This project is a complete Accounting ERP System built with Python, Streamlit, and MySQL/MariaDB. It implements a double-entry bookkeeping system with modules for customers, vendors, employees, products, invoices, journal entries, the general ledger, and financial reporting through an interactive web application.

---

# Features

* Double-Entry Journal System
* Chart of Accounts Management
* Customer & Vendor Management
* Employee Management
* Product & Services Catalog
* Tax Management
* Payment Methods
* Invoice Generation
* Journal Entries
* General Ledger
* Financial Dashboard
* Trial Balance PDF Reports

---

# Prerequisites

* Python 3.13 or higher
* MySQL or MariaDB Server
* uv (Fast Python Package Installer)

---

# Installation

### Install uv (if not already installed)

**Linux/macOS**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows PowerShell**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Windows (Winget)**

```cmd
winget install astral-sh.uv
```

### Clone the repository

```bash
git clone <repository-url>
```

### Navigate to the project directory

```bash
cd Accounting-ERP
```

### Install dependencies

```bash
uv sync
```

---

# Database Setup

1. Start your MySQL/MariaDB server.

2. Create the database using:

```sql
SOURCE accounting.sql;
```

or

```bash
mysql -u root -p < accounting.sql
```

3. If required, update the database connection in `database.py`.

---

# Running the Application

Start the Streamlit application:

```bash
uv run streamlit run app.py
```

Open your browser and visit:

```text
http://localhost:8501
```

---

# Usage Guide

### Dashboard

* View financial metrics
* Monitor account balances
* Download Trial Balance PDF reports

### Chart of Accounts

* Manage account types
* Create new accounts
* View account balances

### Employees

* Add and manage employee records

### Customers

* Add and manage customer information

### Vendors

* Manage supplier records

### Products & Services

* Create and manage products and services

### Taxes

* Configure tax rates

### Payment Methods

* Manage available payment options

### Invoices

* Generate and manage customer invoices

### Journal Entries

* Record balanced accounting transactions

### General Ledger

* View complete transaction history

---

# Screenshots

### Dashboard

<p align="center">
  <img src="YOUR_DASHBOARD_IMAGE" alt="Dashboard" width="900"/>
</p>

---

### Chart of Accounts

<p align="center">
  <img src="YOUR_CHART_OF_ACCOUNTS_IMAGE" alt="Chart of Accounts" width="900"/>
</p>

---

### Customer Management

<p align="center">
  <img src="YOUR_CUSTOMER_IMAGE" alt="Customer Management" width="900"/>
</p>

---

### Vendor Management

<p align="center">
  <img src="YOUR_VENDOR_IMAGE" alt="Vendor Management" width="900"/>
</p>

---

### Product & Services

<p align="center">
  <img src="YOUR_PRODUCT_IMAGE" alt="Products & Services" width="900"/>
</p>

---

### Invoice Management

<p align="center">
  <img src="YOUR_INVOICE_IMAGE" alt="Invoice Management" width="900"/>
</p>

---

### Journal Entries

<p align="center">
  <img src="YOUR_JOURNAL_IMAGE" alt="Journal Entries" width="900"/>
</p>

---

### General Ledger

<p align="center">
  <img src="YOUR_LEDGER_IMAGE" alt="General Ledger" width="900"/>
</p>

---

### Trial Balance Report

<p align="center">
  <img src="YOUR_TRIAL_BALANCE_IMAGE" alt="Trial Balance Report" width="900"/>
</p>

---

# Technologies Used

* Python
* Streamlit
* SQLModel
* MySQL / MariaDB
* SQLAlchemy
* MySQL Connector/Python
* FPDF
* Pandas

---

# Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test the application.
5. Submit a Pull Request.

---

# License

This project is licensed under the MIT License.

---

# Support

If you encounter any issues or have suggestions, feel free to open an issue in this repository.

---

# Created By

<p align="center">
  <a href="https://github.com/MoazzamFarooqui">
    <img src="https://img.shields.io/badge/MoazzamFarooqui-181717?style=for-the-badge&logo=github" alt="MoazzamFarooqui" />
  </a>
  &nbsp;&nbsp;
  <a href="https://github.com/DanyalAbbas">
    <img src="https://img.shields.io/badge/DanyalAbbas-181717?style=for-the-badge&logo=github" alt="DanyalAbbas" />
  </a>
</p>
