import streamlit as st
import pandas as pd
from sqlmodel import Session, select
from database import (
    engine, Account, Customer, Vendor, JournalEntry, JournalItem,
    post_transaction, init_db, AccountType, Employee, Invoice,
    Product, Tax, PaymentMethod
)
from datetime import datetime, date
from fpdf import FPDF
from IncomeStatement import generate_income_statement_pdf, _compute_income_statement


@st.cache_resource
def get_db_engine():
    init_db()
    return engine

try:
    active_engine = get_db_engine()
    st.success("Database initialized successfully!")
except Exception as e:
    st.error(f"Database connection error: {e}")
    st.stop()

st.set_page_config(page_title="Accounting ERP", layout="wide", page_icon="📊")

st.sidebar.markdown("""
<div style="font-family: monospace; white-space: pre; line-height: 1.2; background-color: #0e1117; padding: 10px; border-radius: 5px; color: #ffffff;">
 █████╗ ███████╗██████╗ 
██╔══██╗██╔════╝██╔══██╗
███████║█████╗  ██████╔╝
██╔══██║██╔══╝  ██╔══██╗
██║  ██║███████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝

 <b>ACCOUNTING ERP</b>
 <i>Driven by Precision</i>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.selectbox("Go to", [
    "Dashboard", "Chart of Accounts", "Employees", "Customers", "Vendors",
    "Products & Services", "Taxes", "Payment Methods", "Invoices",
    "Journal Entries", "General Ledger"
])


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_all(model):
    with Session(engine) as session:
        return session.exec(select(model)).all()

def delete_record(model, id_field, record_id):
    with Session(engine) as session:
        record = session.get(model, record_id)
        if record:
            try:
                session.delete(record)
                session.commit()
                return True
            except Exception as e:
                st.error(f"Error deleting record: {e}")
                return False
    return False

def pdf_bytes(pdf):
    output = pdf.output(dest="S")
    if isinstance(output, str):
        return output.encode("latin-1")
    return bytes(output)

def generate_trial_balance_pdf(df_accounts):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Trial Balance Report", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="R")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(30, 10, "Account ID",   1, 0, "C", True)
    pdf.cell(60, 10, "Account Name", 1, 0, "C", True)
    pdf.cell(30, 10, "Type",         1, 0, "C", True)
    pdf.cell(35, 10, "Debit ($)",    1, 0, "C", True)
    pdf.cell(35, 10, "Credit ($)",   1, 1, "C", True)

    pdf.set_font("Arial", "", 10)
    total_debit = total_credit = 0
    for _, row in df_accounts.iterrows():
        balance = row["balance"]
        debit   = balance if balance > 0 else 0
        credit  = abs(balance) if balance < 0 else 0
        pdf.cell(30, 8, str(row["account_id"]), 1)
        pdf.cell(60, 8, row["account_name"],    1)
        pdf.cell(30, 8, row["type"],            1)
        pdf.cell(35, 8, f"{debit:,.2f}",        1, 0, "R")
        pdf.cell(35, 8, f"{credit:,.2f}",       1, 1, "R")
        total_debit  += debit
        total_credit += credit

    pdf.set_font("Arial", "B", 10)
    pdf.cell(120, 10, "TOTAL",                1, 0, "R", True)
    pdf.cell(35,  10, f"{total_debit:,.2f}",  1, 0, "R", True)
    pdf.cell(35,  10, f"{total_credit:,.2f}", 1, 1, "R", True)
    return pdf_bytes(pdf)


# ── Dashboard ─────────────────────────────────────────────────────────────────

if menu == "Dashboard":
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        try:
            st.image("dashboard_logo.png", width=100)
        except:
            st.image("https://cdn-icons-png.flaticon.com/512/2620/2620601.png", width=100)
    with col_title:
        st.markdown("<h1 style='padding-top:20px;'>Accounting Financial Dashboard</h1>",
                    unsafe_allow_html=True)

    accounts      = get_all(Account)
    account_types = get_all(AccountType)
    type_map      = {t.type_id: t.category_name for t in account_types}

    if accounts:
        df_accounts = pd.DataFrame([a.dict() for a in accounts])
        df_accounts["type"] = df_accounts["type_id"].map(type_map).fillna("Unknown")
        tu = df_accounts["type"].str.strip().str.upper()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Assets",      f"${df_accounts[tu == 'ASSET']['balance'].sum():,.2f}")
        col2.metric("Total Liabilities", f"${df_accounts[tu == 'LIABILITY']['balance'].sum():,.2f}")
        col3.metric("Total Equity",      f"${df_accounts[tu == 'EQUITY']['balance'].sum():,.2f}")

        st.subheader("Account Balances")
        st.dataframe(df_accounts[["account_id", "account_name", "type", "balance"]],
                     use_container_width=True)

        st.divider()
        st.subheader("📄 Reports")

        with st.expander("⚙️ Income Statement Settings"):
            is_entity = st.text_input("Entity / Company Name", value="My Company")
            is_period = st.text_input(
                "Period End Date",
                value=datetime.now().strftime("%b %d, %Y").upper()
            )

        col_tb, col_is = st.columns(2)

        with col_tb:
            try:
                st.download_button(
                    label="📄 Download Trial Balance PDF",
                    data=generate_trial_balance_pdf(df_accounts),
                    file_name="Trial_Balance.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating Trial Balance: {e}")

        with col_is:
            try:
                st.download_button(
                    label="📄 Download Income Statement PDF",
                    data=generate_income_statement_pdf(
                        df_accounts,
                        entity_name=is_entity,
                        period_date=is_period,
                        engine=engine          # ← pass engine so we read JournalItems
                    ),
                    file_name="Income_Statement.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating Income Statement: {e}")

        # ── Live Income Statement Preview ──────────────────────────────────
        st.divider()
        st.subheader("📊 Income Statement Preview")

        try:
            d = _compute_income_statement(df_accounts, engine)

            def fmt(val):
                if round(val, 2) == 0: return "$0.00"
                if val < 0: return f"-${abs(val):,.2f}"
                return f"${val:,.2f}"

            op_label  = "═══ Operating Profit ═══" if d["operating_income"] >= 0 else "═══ Operating Loss ═══"
            net_label = "══ Net Profit ══"          if d["net_income"]       >= 0 else "══ Net Loss ══"

            preview = pd.DataFrame({
                "Line Item": [
                    "Total Revenue",
                    "(-) Cost of Sales",
                    "═══ Gross Profit ═══",
                    "(-) Operating Expenses",
                    op_label,
                    "(+) Other Income",
                    net_label,
                ],
                "Amount": [
                    fmt(d["total_revenue"]),
                    f"-${d['cost_of_sales']:,.2f}",
                    fmt(d["gross_profit"]),
                    f"-${d['total_op_expenses']:,.2f}",
                    fmt(d["operating_income"]),
                    fmt(d["total_other_income"]),
                    fmt(d["net_income"]),
                ]
            })
            st.dataframe(preview, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Preview error: {e}")

    else:
        st.info("Start by adding Account Types and Accounts.")


# ── Chart of Accounts ─────────────────────────────────────────────────────────

elif menu == "Chart of Accounts":
    st.title("📂 Chart of Accounts")

    with st.expander("⚙️ Manage Account Types"):
        types = get_all(AccountType)
        if types:
            st.table(pd.DataFrame([t.dict() for t in types]))
        with st.form("add_type"):
            new_type = st.text_input("New Category Name (e.g., Asset, Expense)")
            if st.form_submit_button("Add Category"):
                with Session(engine) as session:
                    session.add(AccountType(category_name=new_type))
                    session.commit()
                    st.rerun()
        if types:
            with st.form("delete_type"):
                type_to_del = st.selectbox(
                    "Select Type to Delete",
                    options=[t.type_id for t in types],
                    format_func=lambda x: next(t.category_name for t in types if t.type_id == x)
                )
                if st.form_submit_button("🗑️ Delete Account Type"):
                    if delete_record(AccountType, "type_id", type_to_del):
                        st.success("Account Type deleted!")
                        st.rerun()

    accounts      = get_all(Account)
    account_types = get_all(AccountType)
    type_options  = {t.type_id: t.category_name for t in account_types}

    if accounts:
        df = pd.DataFrame([a.dict() for a in accounts])
        df["type"] = df["type_id"].map(type_options)
        st.dataframe(df[["account_id", "account_name", "account_code", "type", "balance"]],
                     use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("➕ Add New Account"):
            with st.form("add_account"):
                acc_id   = st.number_input("Account ID (e.g. 1010)", step=1)
                acc_name = st.text_input("Account Name")
                acc_code = st.text_input("Account Code")
                acc_type = st.selectbox("Account Type",
                                        options=list(type_options.keys()),
                                        format_func=lambda x: type_options[x])
                if st.form_submit_button("Create Account"):
                    with Session(engine) as session:
                        session.add(Account(account_id=acc_id, account_name=acc_name,
                                            account_code=acc_code, type_id=acc_type))
                        session.commit()
                        st.rerun()
    with col2:
        if accounts:
            with st.expander("🗑️ Delete Account"):
                with st.form("delete_account"):
                    acc_to_del = st.selectbox(
                        "Select Account to Delete",
                        options=[a.account_id for a in accounts],
                        format_func=lambda x: f"{x} - {next(a.account_name for a in accounts if a.account_id == x)}"
                    )
                    if st.form_submit_button("🗑️ Delete Account"):
                        if delete_record(Account, "account_id", acc_to_del):
                            st.success("Account deleted!")
                            st.rerun()


# ── Employees ─────────────────────────────────────────────────────────────────

elif menu == "Employees":
    st.title("👨‍💼 Employee Management")
    employees = get_all(Employee)
    if employees:
        st.dataframe(pd.DataFrame([e.dict() for e in employees]), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("➕ Add New Employee"):
            with st.form("add_emp"):
                name   = st.text_input("Name")
                role   = st.text_input("Role")
                dept   = st.text_input("Department")
                h_date = st.date_input("Hire Date")
                if st.form_submit_button("Add Employee"):
                    with Session(engine) as session:
                        session.add(Employee(name=name, role=role, department=dept, hire_date=h_date))
                        session.commit()
                        st.rerun()
    with col2:
        if employees:
            with st.expander("🗑️ Delete Employee"):
                with st.form("delete_employee"):
                    emp_to_del = st.selectbox(
                        "Select Employee to Delete",
                        options=[e.employee_id for e in employees],
                        format_func=lambda x: next(e.name for e in employees if e.employee_id == x)
                    )
                    if st.form_submit_button("🗑️ Delete Employee"):
                        if delete_record(Employee, "employee_id", emp_to_del):
                            st.success("Employee deleted!")
                            st.rerun()


# ── Customers ─────────────────────────────────────────────────────────────────

elif menu == "Customers":
    st.title("👥 Customer Management")
    customers = get_all(Customer)
    if customers:
        st.dataframe(pd.DataFrame([c.dict() for c in customers]), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("➕ Add New Customer"):
            with st.form("add_cust"):
                name  = st.text_input("Customer Name")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                if st.form_submit_button("Add Customer"):
                    with Session(engine) as session:
                        session.add(Customer(name=name, email=email, phone=phone))
                        session.commit()
                        st.rerun()
    with col2:
        if customers:
            with st.expander("🗑️ Delete Customer"):
                with st.form("delete_customer"):
                    cust_to_del = st.selectbox(
                        "Select Customer to Delete",
                        options=[c.customer_id for c in customers],
                        format_func=lambda x: next(c.name for c in customers if c.customer_id == x)
                    )
                    if st.form_submit_button("🗑️ Delete Customer"):
                        if delete_record(Customer, "customer_id", cust_to_del):
                            st.success("Customer deleted!")
                            st.rerun()


# ── Vendors ───────────────────────────────────────────────────────────────────

elif menu == "Vendors":
    st.title("🏭 Vendor Management")
    vendors = get_all(Vendor)
    if vendors:
        st.dataframe(pd.DataFrame([v.dict() for v in vendors]), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("➕ Add New Vendor"):
            with st.form("add_vend"):
                name    = st.text_input("Company Name")
                contact = st.text_input("Contact")
                tax_id  = st.text_input("Tax ID")
                if st.form_submit_button("Add Vendor"):
                    with Session(engine) as session:
                        session.add(Vendor(company_name=name, contact=contact, tax_id=tax_id))
                        session.commit()
                        st.rerun()
    with col2:
        if vendors:
            with st.expander("🗑️ Delete Vendor"):
                with st.form("delete_vendor"):
                    ven_to_del = st.selectbox(
                        "Select Vendor to Delete",
                        options=[v.vendor_id for v in vendors],
                        format_func=lambda x: next(v.company_name for v in vendors if v.vendor_id == x)
                    )
                    if st.form_submit_button("🗑️ Delete Vendor"):
                        if delete_record(Vendor, "vendor_id", ven_to_del):
                            st.success("Vendor deleted!")
                            st.rerun()


# ── Products & Services ───────────────────────────────────────────────────────

elif menu == "Products & Services":
    st.title("📦 Products & Services")
    products = get_all(Product)
    if products:
        st.dataframe(pd.DataFrame([p.dict() for p in products]), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("➕ Add New Product"):
            with st.form("add_prod"):
                name  = st.text_input("Product Name")
                price = st.number_input("Unit Price", min_value=0.0)
                cat   = st.text_input("Category")
                if st.form_submit_button("Add Product"):
                    with Session(engine) as session:
                        session.add(Product(name=name, unit_price=price, category=cat))
                        session.commit()
                        st.rerun()
    with col2:
        if products:
            with st.expander("🗑️ Delete Product"):
                with st.form("delete_product"):
                    prod_to_del = st.selectbox(
                        "Select Product to Delete",
                        options=[p.product_id for p in products],
                        format_func=lambda x: next(p.name for p in products if p.product_id == x)
                    )
                    if st.form_submit_button("🗑️ Delete Product"):
                        if delete_record(Product, "product_id", prod_to_del):
                            st.success("Product deleted!")
                            st.rerun()


# ── Taxes ─────────────────────────────────────────────────────────────────────

elif menu == "Taxes":
    st.title("⚖️ Tax Configuration")
    taxes = get_all(Tax)
    if taxes:
        st.dataframe(pd.DataFrame([t.dict() for t in taxes]), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("➕ Add New Tax"):
            with st.form("add_tax"):
                name = st.text_input("Tax Name")
                perc = st.number_input("Percentage", min_value=0.0, max_value=100.0)
                if st.form_submit_button("Add Tax"):
                    with Session(engine) as session:
                        session.add(Tax(tax_name=name, percentage=perc))
                        session.commit()
                        st.rerun()
    with col2:
        if taxes:
            with st.expander("🗑️ Delete Tax"):
                with st.form("delete_tax"):
                    tax_to_del = st.selectbox(
                        "Select Tax to Delete",
                        options=[t.tax_id for t in taxes],
                        format_func=lambda x: next(t.tax_name for t in taxes if t.tax_id == x)
                    )
                    if st.form_submit_button("🗑️ Delete Tax"):
                        if delete_record(Tax, "tax_id", tax_to_del):
                            st.success("Tax deleted!")
                            st.rerun()


# ── Payment Methods ───────────────────────────────────────────────────────────

elif menu == "Payment Methods":
    st.title("💳 Payment Methods")
    methods = get_all(PaymentMethod)
    if methods:
        st.dataframe(pd.DataFrame([m.dict() for m in methods]), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("➕ Add New Payment Method"):
            with st.form("add_pm"):
                name = st.text_input("Method Name (e.g. Cash, Credit Card)")
                if st.form_submit_button("Add Method"):
                    with Session(engine) as session:
                        session.add(PaymentMethod(method_name=name))
                        session.commit()
                        st.rerun()
    with col2:
        if methods:
            with st.expander("🗑️ Delete Payment Method"):
                with st.form("delete_pm"):
                    pm_to_del = st.selectbox(
                        "Select Payment Method to Delete",
                        options=[m.payment_id for m in methods],
                        format_func=lambda x: next(m.method_name for m in methods if m.payment_id == x)
                    )
                    if st.form_submit_button("🗑️ Delete Payment Method"):
                        if delete_record(PaymentMethod, "payment_id", pm_to_del):
                            st.success("Payment Method deleted!")
                            st.rerun()


# ── Invoices ──────────────────────────────────────────────────────────────────

elif menu == "Invoices":
    st.title("🧾 Invoices")
    invoices  = get_all(Invoice)
    customers = get_all(Customer)
    employees = get_all(Employee)
    cust_map  = {c.customer_id: c.name for c in customers}
    emp_map   = {e.employee_id: e.name for e in employees}

    if invoices:
        df = pd.DataFrame([i.dict() for i in invoices])
        df["customer"] = df["customer_id"].map(cust_map)
        df["employee"] = df["employee_id"].map(emp_map)
        st.dataframe(df[["invoice_id", "date", "total", "status", "customer", "employee"]],
                     use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("➕ Create New Invoice"):
            with st.form("add_invoice"):
                inv_date = st.date_input("Invoice Date")
                total    = st.number_input("Total Amount", min_value=0.0)
                status   = st.selectbox("Status", ["Draft", "Sent", "Paid", "Cancelled"])
                cust_id  = st.selectbox("Customer", options=list(cust_map.keys()),
                                        format_func=lambda x: cust_map[x])
                emp_id   = st.selectbox("Assigned Employee", options=list(emp_map.keys()),
                                        format_func=lambda x: emp_map[x])
                if st.form_submit_button("Create Invoice"):
                    with Session(engine) as session:
                        session.add(Invoice(date=inv_date, total=total, status=status,
                                            customer_id=cust_id, employee_id=emp_id))
                        session.commit()
                        st.rerun()
    with col2:
        if invoices:
            with st.expander("🗑️ Delete Invoice"):
                with st.form("delete_invoice"):
                    inv_to_del = st.selectbox(
                        "Select Invoice to Delete",
                        options=[i.invoice_id for i in invoices],
                        format_func=lambda x: f"Inv #{x} - {cust_map.get(next(inv.customer_id for inv in invoices if inv.invoice_id == x), 'Unknown')}"
                    )
                    if st.form_submit_button("🗑️ Delete Invoice"):
                        if delete_record(Invoice, "invoice_id", inv_to_del):
                            st.success("Invoice deleted!")
                            st.rerun()


# ── Journal Entries ───────────────────────────────────────────────────────────

elif menu == "Journal Entries":
    st.title("✍️ Journal Entry (Double Entry)")

    accounts  = get_all(Account)
    employees = get_all(Employee)
    invoices  = get_all(Invoice)
    vendors   = get_all(Vendor)
    methods   = get_all(PaymentMethod)
    products  = get_all(Product)
    taxes     = get_all(Tax)

    if not accounts:
        st.warning("Please create accounts first.")
    else:
        with st.form("journal_entry_form"):
            col1, col2 = st.columns(2)
            desc   = col1.text_input("Description")
            status = col2.selectbox("Status", ["Draft", "Posted", "Void"])

            c1, c2, c3, c4 = st.columns(4)
            emp_map = {e.employee_id: e.name for e in employees};       emp_map[0] = "None"
            inv_map = {i.invoice_id: f"Inv #{i.invoice_id}" for i in invoices}; inv_map[0] = "None"
            ven_map = {v.vendor_id: v.company_name for v in vendors};   ven_map[0] = "None"
            pay_map = {m.payment_id: m.method_name for m in methods};   pay_map[0] = "None"

            emp_id = c1.selectbox("Created By",     options=list(emp_map.keys()), format_func=lambda x: emp_map[x])
            inv_id = c2.selectbox("Linked Invoice", options=list(inv_map.keys()), format_func=lambda x: inv_map[x])
            ven_id = c3.selectbox("Linked Vendor",  options=list(ven_map.keys()), format_func=lambda x: ven_map[x])
            pay_id = c4.selectbox("Payment Method", options=list(pay_map.keys()), format_func=lambda x: pay_map[x])

            st.divider()
            st.subheader("Entry Items")
            num_lines = st.number_input("Number of Items", min_value=2, max_value=20, value=2)

            ledger_lines    = []
            account_options = {a.account_id: f"{a.account_id} - {a.account_name}" for a in accounts}
            prod_map = {p.product_id: p.name for p in products}; prod_map[0] = "None"
            tax_map  = {t.tax_id: f"{t.tax_name} ({t.percentage}%)" for t in taxes}; tax_map[0] = "None"

            for i in range(num_lines):
                r1, r2, r3, r4, r5 = st.columns([3, 2, 2, 2, 2])
                acc_id = r1.selectbox(f"Account {i+1}", options=list(account_options.keys()),
                                      format_func=lambda x: account_options[x], key=f"acc_{i}")
                deb    = r2.number_input(f"Debit {i+1}",  min_value=0.0, format="%.2f", key=f"deb_{i}")
                cre    = r3.number_input(f"Credit {i+1}", min_value=0.0, format="%.2f", key=f"cre_{i}")
                p_id   = r4.selectbox(f"Product {i+1}", options=list(prod_map.keys()),
                                      format_func=lambda x: prod_map[x], key=f"prod_{i}")
                t_id   = r5.selectbox(f"Tax {i+1}", options=list(tax_map.keys()),
                                      format_func=lambda x: tax_map[x], key=f"tax_{i}")
                ledger_lines.append({
                    "account_id": acc_id, "debit": deb, "credit": cre,
                    "product_id": p_id if p_id > 0 else None,
                    "tax_id":     t_id if t_id > 0 else None
                })

            if st.form_submit_button("Post Journal Entry"):
                res = post_transaction(
                    description=desc, ledger_lines=ledger_lines,
                    employee_id=emp_id if emp_id > 0 else None,
                    invoice_id =inv_id if inv_id > 0 else None,
                    vendor_id  =ven_id if ven_id > 0 else None,
                    payment_id =pay_id if pay_id > 0 else None,
                    status=status
                )
                if res == "Success":
                    st.success("Journal Entry posted!")
                else:
                    st.error(res)

        entries = get_all(JournalEntry)
        if entries:
            with st.expander("🗑️ Delete Journal Entry"):
                with st.form("delete_entry"):
                    entry_to_del = st.selectbox(
                        "Select Entry to Delete",
                        options=[e.entry_id for e in entries],
                        format_func=lambda x: f"ID {x} - {next(e.description for e in entries if e.entry_id == x)}"
                    )
                    if st.form_submit_button("🗑️ Delete Journal Entry"):
                        with Session(engine) as session:
                            items = session.exec(
                                select(JournalItem).where(JournalItem.entry_id == entry_to_del)
                            ).all()
                            for item in items:
                                session.delete(item)
                            session.commit()
                        if delete_record(JournalEntry, "entry_id", entry_to_del):
                            st.success("Journal Entry and its items deleted!")
                            st.rerun()


# ── General Ledger ────────────────────────────────────────────────────────────

elif menu == "General Ledger":
    st.title("📖 General Ledger")
    with Session(engine) as session:
        statement = (
            select(JournalItem, Account.account_name,
                   JournalEntry.date, JournalEntry.description)
            .join(Account,      JournalItem.account_id == Account.account_id)
            .join(JournalEntry, JournalItem.entry_id   == JournalEntry.entry_id)
            .order_by(JournalEntry.date.desc())
        )
        results = session.exec(statement).all()

        if results:
            data = []
            for item, acc_name, date_val, desc in results:
                data.append({
                    "Date":        date_val.strftime("%Y-%m-%d %H:%M"),
                    "Entry ID":    item.entry_id,
                    "Line":        item.line_no,
                    "Account":     f"{item.account_id} - {acc_name}",
                    "Description": desc,
                    "Debit":       item.debit,
                    "Credit":      item.credit
                })
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info("No ledger entries found.")
