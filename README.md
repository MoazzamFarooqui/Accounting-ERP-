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

## Dashboard

<img width="595" height="268" alt="image" src="https://github.com/user-attachments/assets/e1763761-6caa-46d5-9519-6fae68a6a5b8" />

### Generation of PDF files of Trial Balance, Income Statement and Balance Sheet:

<img width="598" height="262" alt="image" src="https://github.com/user-attachments/assets/627b5422-b4cc-484f-9e8a-c245c1fe01ef" />

<img width="595" height="188" alt="image" src="https://github.com/user-attachments/assets/0e515868-4aa3-4270-b1fd-77841a9ee501" />

---

## Chart of Accounts

<img width="599" height="261" alt="image" src="https://github.com/user-attachments/assets/7d1ce193-bdc3-4845-8be5-bdd44c704897" />

### Features of Adding and Deleting the Account

<img width="594" height="212" alt="image" src="https://github.com/user-attachments/assets/a55ce534-c6f9-4e70-93da-5ca88a439f24" />

---

## Employees

<img width="587" height="163" alt="image" src="https://github.com/user-attachments/assets/50e87e20-7885-4710-a321-effd62f1dfda" />

### Features of Adding and Deleting Employees

<img width="601" height="171" alt="image" src="https://github.com/user-attachments/assets/2db52e6e-83fc-470e-81bc-9c2e0ef05b82" />

---

## Customers 

<img width="596" height="156" alt="image" src="https://github.com/user-attachments/assets/09620dfb-1678-4a00-b5ce-4ab0ca7a9bda" />

### Features of Adding and Deleting Customers

<img width="602" height="170" alt="image" src="https://github.com/user-attachments/assets/28264b33-77be-4807-ac7d-cffc9f315274" />

---

## Vendors

<img width="600" height="175" alt="image" src="https://github.com/user-attachments/assets/e19581f6-304b-4716-8224-af1de1308ae6" />

### Features of Adding and Deleting Vendors

<img width="599" height="171" alt="image" src="https://github.com/user-attachments/assets/8d532217-e662-4792-8dc8-6150d24433b7" />

---

## Product & Services

<img width="601" height="141" alt="image" src="https://github.com/user-attachments/assets/a0fc54dd-384d-4edb-92ba-26cc2609987a" />

### Features of Adding a New Product

<img width="600" height="312" alt="image" src="https://github.com/user-attachments/assets/82713792-f9f3-47ae-8685-a27ddcd22971" />

---

## Taxes

<img width="595" height="149" alt="image" src="https://github.com/user-attachments/assets/65e10f77-392a-4192-aef3-f3c4e0a1aa3c" />

### Feature of Adding the Tax name & Percentage

<img width="601" height="270" alt="image" src="https://github.com/user-attachments/assets/6885594b-b9dd-4ce3-9c09-a4aa92f3a5b8" />

---

## Payment Methods

<img width="599" height="197" alt="image" src="https://github.com/user-attachments/assets/53a3cdb6-9f3c-4a8f-a3f1-f9023a5af36f" />

### Features of Adding and Deleting Payment Methods

<img width="607" height="107" alt="image" src="https://github.com/user-attachments/assets/c7ccef7a-0aef-4ffe-a193-d18571b01b99" />

---

## Invoices

<img width="607" height="124" alt="image" src="https://github.com/user-attachments/assets/9a5a93a2-91b6-4bd5-8da1-502fa23a8bf9" />

### Features of Creating Invoices

<img width="602" height="453" alt="image" src="https://github.com/user-attachments/assets/af2a8451-8a28-4e30-b0cf-0be496903d8e" />

---

## Journal Entries

<img width="597" height="289" alt="image" src="https://github.com/user-attachments/assets/b91b12b5-657f-417f-a9a2-cfadfe3abe84" />

### Feature of Deleting the Journal Entry

<img width="605" height="121" alt="image" src="https://github.com/user-attachments/assets/7dd64c26-a292-4e40-bd39-53bebde52f55" />

---

## General Ledger

<img width="601" height="173" alt="image" src="https://github.com/user-attachments/assets/11ee21ec-26aa-488e-92f1-aadf464374c0" />

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
