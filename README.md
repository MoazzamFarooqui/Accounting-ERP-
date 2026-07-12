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

<img width="1548" height="607" alt="image" src="https://github.com/user-attachments/assets/2d38cdbc-e876-4b9a-ab7d-01a0151f3bfd" />

<img width="1522" height="222" alt="image" src="https://github.com/user-attachments/assets/a5f4f9c6-3973-4b91-a106-e886164adb98" />

<img width="1515" height="353" alt="image" src="https://github.com/user-attachments/assets/a2b2f694-3f23-4467-9cf4-27ead9e0de21" />

<img width="1535" height="430" alt="image" src="https://github.com/user-attachments/assets/f3427699-95ad-40eb-b5af-191dac826d43" />

---

## Chart Of Accounts

<img width="1538" height="507" alt="image" src="https://github.com/user-attachments/assets/ef3740ac-2057-4b59-98e8-750c03f6b8df" />

---

## Employee Management

<img width="1547" height="431" alt="image" src="https://github.com/user-attachments/assets/c4bfa896-0eb4-40b1-bf9b-7bfce71165ca" />

---

## Customer Management

<img width="1552" height="418" alt="image" src="https://github.com/user-attachments/assets/4c6f945e-4a5a-4d31-b400-a26085baecb1" />

---

## Vendor Management

<img width="1547" height="435" alt="image" src="https://github.com/user-attachments/assets/85c5a2a4-f214-4cf0-8099-d4f38dc174d8" />

---

## Products & Services

<img width="1548" height="412" alt="image" src="https://github.com/user-attachments/assets/ea89e307-a8f5-4aba-8d41-be379bd93647" />

---

## Tax Configuration

<img width="1530" height="407" alt="image" src="https://github.com/user-attachments/assets/fce65f6a-c07a-42cc-a66c-c801a417baff" />

---

## Payment Methods

<img width="1536" height="472" alt="image" src="https://github.com/user-attachments/assets/0d77099b-426a-4c86-a8bb-8808be0262c2" />

---

## Invoices

<img width="1535" height="397" alt="image" src="https://github.com/user-attachments/assets/a17450d9-8b43-47f8-92e1-309b4420c848" />

---

## Journal Entries

<img width="1537" height="837" alt="image" src="https://github.com/user-attachments/assets/eb327b84-2a4a-45d5-8dae-8b03ca506dce" />

---

## General Ledger

<img width="1547" height="327" alt="image" src="https://github.com/user-attachments/assets/ee1977ba-d876-4c78-a81d-22d69b8f9638" />

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
</p> i want proper headings in screenshot section
