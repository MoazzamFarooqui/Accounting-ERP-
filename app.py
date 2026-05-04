import streamlit as st
import pandas as pd
from sqlmodel import Session, select
from database import (
    engine, Account, Customer, Vendor, JournalEntry, JournalItem,
    post_transaction, init_db, AccountType, Employee, Invoice,
    Product, Tax, PaymentMethod, reverse_transaction, recalculate_all_balances
)
from datetime import datetime, date
from fpdf import FPDF
from IncomeStatement import generate_income_statement_pdf
from BalanceSheet import generate_balance_sheet_pdf, prepare_balance_sheet_data


@st.cache_resource
def get_db_engine():
    init_db()
    return engine

try:
    active_engine = get_db_engine()
    print("yiopeee")
except Exception as e:
    st.error(f"Database connection error: {e}")
    st.stop()

st.set_page_config(page_title="DunixStore ERP", layout="wide")

st.markdown("""
<style>
:root {
    color-scheme: light;
    font-family: Inter, system-ui, sans-serif;
}
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left, rgba(59,130,246,0.14), transparent 18%),
                radial-gradient(circle at 85% 10%, rgba(16,185,129,0.1), transparent 20%),
                #f8fafc;
}
[data-testid="stSidebar"] {
    background: #ffffff;
    color: #0f172a;
}
[data-testid="stSidebar"] .css-1d391kg,
[data-testid="stSidebar"] .css-1ihfar8 {
    background: transparent;
}
.stApp .css-1nf9yta e {
    color: #0f172a;
}
section[data-testid="stSidebar"] .css-1aot0al {
    background: #ffffff;
}
.css-10trblm {
    background: rgba(255,255,255,0.9);
    border: 1px solid rgba(148,163,184,0.2);
    border-radius: 24px;
}
.css-1aumxhk {
    color: #0f172a;
}
button {
    border-radius: 999px !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%) !important;
    color: #fff !important;
    border: none !important;
}
button[kind="secondary"] {
    border: 1px solid rgba(15,23,42,0.12) !important;
    color: #0f172a !important;
    background: rgba(255,255,255,0.9) !important;
}
</style>
""", unsafe_allow_html=True)


def render_page_header(title, subtitle, icon=""):
    st.markdown(f"""
    <div style='border-radius: 24px; padding: 28px; margin-bottom: 24px;
                background: linear-gradient(135deg, rgba(56,189,248,0.12), rgba(236,253,245,0.95));
                box-shadow: 0 20px 40px rgba(15,23,42,0.08);'>
        <div style='display:flex; align-items:center; gap:16px;'>
            <div style='font-size: 2.4rem; background: linear-gradient(135deg, #22d3ee, #2563eb);
                        width: 72px; height: 72px; display:flex; align-items:center;
                        justify-content:center; border-radius: 18px; color: #ffffff;'>
                {icon}
            </div>
            <div>
                <h1 style='margin:0; color:#0f172a; font-size:2.2rem;'>{title}</h1>
                <p style='margin:6px 0 0; color:#475569; font-size:1rem;'>{subtitle}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_card(title, value, subtitle=""):
    st.markdown(f"""
    <div style='border-radius: 20px; background: rgba(255,255,255,0.92);
                border: 1px solid rgba(148,163,184,0.2); padding: 20px; min-height: 115px;'>
        <div style='font-size: 0.85rem; color: #64748b; margin-bottom: 8px;'>{title}</div>
        <div style='font-size: 1.8rem; font-weight: 700; color: #0f172a;'>{value}</div>
        <div style='color: #64748b; margin-top: 6px; font-size: 0.95rem;'>
            {subtitle}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="font-family: Inter, sans-serif; background-color: #ffffff; padding: 18px; border-radius: 18px; border: 1px solid rgba(15,23,42,0.08); color: #0f172a;">
    <div style="font-size: 1.3rem; font-weight: 700; margin-bottom: 8px;">DunixStore ERP</div>
    <div style="font-size: 0.92rem; color: #475569; line-height: 1.5;">
    </div>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard", "Chart of Accounts", "Employees", "Customers", "Vendors",
        "Products & Services", "Taxes", "Payment Methods", "Invoices",
        "Journal Entries", "General Ledger"
    ],
    key="sidebar_menu"
)


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
    """
    Reads SUM(debit) and SUM(credit) per account directly from JournalItem.
    This is the only correct way — Account.balance is unreliable for column splits.
    Debit total MUST equal Credit total for balanced books.
    """
    with Session(engine) as session:
        items = session.exec(select(JournalItem)).all()

    if items:
        ji_df = pd.DataFrame([{
            "account_id": i.account_id,
            "debit":      i.debit  or 0.0,
            "credit":     i.credit or 0.0,
        } for i in items])
        ji_df = ji_df.groupby("account_id").agg(
            total_debit  =("debit",  "sum"),
            total_credit =("credit", "sum"),
        ).reset_index()
    else:
        ji_df = pd.DataFrame(columns=["account_id", "total_debit", "total_credit"])

    df = df_accounts.copy()
    df = df.merge(ji_df, on="account_id", how="left")
    df["total_debit"]  = df["total_debit"].fillna(0.0)
    df["total_credit"] = df["total_credit"].fillna(0.0)

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
    grand_debit = grand_credit = 0.0

    for _, row in df.iterrows():
        d = float(row["total_debit"])
        c = float(row["total_credit"])
        pdf.cell(30, 8, str(row["account_id"]),   1)
        pdf.cell(60, 8, str(row["account_name"]), 1)
        pdf.cell(30, 8, str(row["type"]),         1)
        pdf.cell(35, 8, f"{d:,.2f}",              1, 0, "R")
        pdf.cell(35, 8, f"{c:,.2f}",              1, 1, "R")
        grand_debit  += d
        grand_credit += c

    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(120, 10, "TOTAL",                 1, 0, "R", True)
    pdf.cell(35,  10, f"{grand_debit:,.2f}",   1, 0, "R", True)
    pdf.cell(35,  10, f"{grand_credit:,.2f}",  1, 1, "R", True)

    pdf.ln(4)
    pdf.set_font("Arial", "I", 9)
    diff = abs(grand_debit - grand_credit)
    if diff < 0.01:
        pdf.set_text_color(0, 150, 0)
        pdf.cell(0, 6, "  Balanced: Total Debit = Total Credit", 0, 1, "C")
    else:
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 6, f"  Out of balance by ${diff:,.2f} — check journal entries", 0, 1, "C")
    pdf.set_text_color(0, 0, 0)

    return pdf_bytes(pdf)


# ── Dashboard ─────────────────────────────────────────────────────────────────

if menu == "Dashboard":
    render_page_header(
        title="Accounting Financial Dashboard",
        subtitle="Monitor assets, liabilities, equity, and reports from a unified modern workspace.",
        icon="📈"
    )

    accounts = get_all(Account)
    account_types = get_all(AccountType)
    type_map      = {t.type_id: t.category_name for t in account_types}

    if accounts:
        df_accounts = pd.DataFrame([a.dict() for a in accounts])
        df_accounts["type"] = df_accounts["type_id"].map(type_map).fillna("Unknown")

        # ── ALWAYS recompute balance from JournalItems — ignore stale DB values ──
        with Session(engine) as _s:
            _all_items = _s.exec(select(JournalItem)).all()
        if _all_items:
            _ji = pd.DataFrame([{
                "account_id": i.account_id,
                "debit":      i.debit  or 0.0,
                "credit":     i.credit or 0.0
            } for i in _all_items])
            _ji = _ji.groupby("account_id").agg(
                _d=("debit", "sum"), _c=("credit", "sum")
            ).reset_index()
            _ji["balance"] = _ji["_d"] - _ji["_c"]
            df_accounts = df_accounts.drop(columns=["balance"]).merge(
                _ji[["account_id", "balance"]], on="account_id", how="left"
            )
        df_accounts["balance"] = df_accounts["balance"].fillna(0.0)

        tu = df_accounts["type"].str.strip().str.upper()

        asset_total = df_accounts[tu == 'ASSET']['balance'].sum()
        liability_total = abs(df_accounts[tu == 'LIABILITY']['balance'].sum())
        equity_total = abs(df_accounts[tu == 'EQUITY']['balance'].sum())

        col1, col2, col3 = st.columns(3)
        with col1:
            render_card("Total Assets", f"${asset_total:,.2f}", "Computed from ledger balances")
        with col2:
            render_card("Total Liabilities", f"${liability_total:,.2f}", "Includes all liability accounts")
        with col3:
            render_card("Total Equity", f"${equity_total:,.2f}", "Equity accounts and retained earnings")

        st.subheader("Account Balances")
        st.dataframe(df_accounts[["account_id", "account_name", "type", "balance"]],
                     use_container_width=True)

        st.divider()
        st.subheader("📄 Reports")

        with st.expander("⚙️ Financial Statement Settings"):
            is_entity = st.text_input("Entity / Company Name", value="DunixStore Inc.")
            is_period = st.text_input(
                "Period End Date",
                value=datetime.now().strftime("%b %d, %Y").upper()
            )
        col_tb, col_is, col_bs = st.columns(3)

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
                        period_date=is_period
                    ),
                    file_name="Income_Statement.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating Income Statement: {e}")

        with col_bs:
            try:
                st.download_button(
                    label="📄 Download Balance Sheet PDF",
                    data=generate_balance_sheet_pdf(
                        df_accounts,
                        entity_name=is_entity,
                        as_of_date=is_period
                    ),
                    file_name="Balance_Sheet.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating Balance Sheet: {e}")

        # ── Live Income Statement Preview ──────────────────────────────────
        st.divider()
        st.subheader("💲 Income Statement Preview")

        REVENUE_TYPES      = {"REVENUE", "INCOME", "SALES", "SALE"}
        OTHER_INC_TYPES    = {"OTHER INCOME", "NON-OPERATING INCOME",
                              "INTEREST INCOME", "DIVIDEND INCOME", "GAIN"}
        COGS_NAME_KEYWORDS = ("PURCHASE", "COST OF GOOD", "COGS", "INVENTORY COST",
                              "DIRECT MATERIAL", "DIRECT LABOUR", "DIRECT LABOR",
                              "FREIGHT IN", "CLOSING STOCK", "OPENING STOCK",
                              "BEGINNING INVENTORY", "ENDING INVENTORY")

        df = df_accounts.copy()
        df["type_upper"] = df["type"].str.strip().str.upper()
        df["name_upper"] = df["account_name"].str.strip().str.upper()

        rev_df        = df[df["type_upper"].isin(REVENUE_TYPES)]
        total_revenue = rev_df["balance"].abs().sum()

        cogs_mask = (
            df["type_upper"].isin({"COGS", "COST OF SALES", "COST OF GOODS", "PURCHASES"}) |
            (df["name_upper"].apply(lambda n: any(k in n for k in COGS_NAME_KEYWORDS)) &
             (df["type_upper"] == "EXPENSE"))
        )
        cogs_df  = df[cogs_mask]
        cogs_ids = set(cogs_df.index)

        opening   = abs(cogs_df[cogs_df["name_upper"].str.contains("OPENING|BEGINNING", na=False)]["balance"].sum())
        purchases = abs(cogs_df[~cogs_df["name_upper"].str.contains("OPENING|BEGINNING|CLOSING|ENDING", na=False)]["balance"].sum())
        closing   = abs(cogs_df[cogs_df["name_upper"].str.contains("CLOSING|ENDING", na=False)]["balance"].sum())
        if closing == 0:
            closing = abs(df[df["name_upper"].str.contains("INVENTORY|STOCK", na=False) &
                             (df["type_upper"] == "ASSET")]["balance"].sum())

        cogs_total   = max(0.0, (opening + purchases) - closing)
        gross_profit = total_revenue - cogs_total

        op_exp_df = df[(df["type_upper"] == "EXPENSE") & (~df.index.isin(cogs_ids))].copy()
        op_exp_df["balance"] = op_exp_df["balance"].abs()
        total_op_exp = op_exp_df["balance"].sum()
        op_income    = gross_profit - total_op_exp

        other_inc  = df[df["type_upper"].isin(OTHER_INC_TYPES)]["balance"].abs().sum()
        net_income = op_income + other_inc

        def fmt(val):
            if round(val, 2) == 0: return "$0.00"
            if val < 0: return f"-${abs(val):,.2f}"
            return f"${val:,.2f}"

        op_label  = "═══ Operating Profit ═══" if op_income  >= 0 else "═══ Operating Loss ═══"
        net_label = "══ Net Profit ══"          if net_income >= 0 else "══ Net Loss ══"

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
                fmt(total_revenue),
                f"-${cogs_total:,.2f}",
                fmt(gross_profit),
                f"-${total_op_exp:,.2f}",
                fmt(abs(op_income)),
                fmt(other_inc),
                fmt(abs(net_income)),
            ]
        })
        st.dataframe(preview, use_container_width=True, hide_index=True)

        # ── Live Balance Sheet Preview ─────────────────────────────────────
        st.divider()
        st.subheader("📘 Balance Sheet Preview")

        try:
            bs_data = prepare_balance_sheet_data(df_accounts)

            def fmt_bs(val):
                if round(val, 2) == 0: return "$0.00"
                if val < 0: return f"(${abs(val):,.2f})"
                return f"${val:,.2f}"

            bs_preview = pd.DataFrame({
                "Line Item": [
                    "Total Assets",
                    "Total Liabilities",
                    "Equity (Capital Accounts)",
                    "Current Year Earnings",
                    "Total Equity",
                    "Total Liabilities + Equity",
                    "Difference",
                ],
                "Amount": [
                    fmt_bs(bs_data["total_assets"]),
                    fmt_bs(bs_data["total_liabilities"]),
                    fmt_bs(bs_data["base_equity_total"]),
                    fmt_bs(bs_data["current_earnings"]),
                    fmt_bs(bs_data["total_equity"]),
                    fmt_bs(bs_data["liabilities_and_equity_total"]),
                    fmt_bs(bs_data["difference"]),
                ]
            })
            st.dataframe(bs_preview, use_container_width=True, hide_index=True)

            if abs(bs_data["difference"]) <= 0.01:
                st.success("✓ Balance Sheet is balanced: Assets = Liabilities + Equity")
            else:
                st.warning(f"⚠ Out of balance by ${abs(bs_data['difference']):,.2f} — review journal entries.")
        except Exception as e:
            st.error(f"Balance Sheet preview error: {e}")

    else:
        st.info("Start by adding Account Types and Accounts.")


# ── Chart of Accounts ─────────────────────────────────────────────────────────

elif menu == "Chart of Accounts":
    render_page_header(
        title="Chart of Accounts",
        subtitle="Create and manage account types, codes, and balances with better visibility.",
        icon="📂"
    )

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
    render_page_header(
        title="Employee Management",
        subtitle="Track your team, roles, and hiring information in one place.",
        icon="👨‍💼"
    )
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
    render_page_header(
        title="Customer Management",
        subtitle="Manage customer records, communication details, and invoicing relationships.",
        icon="👥"
    )
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
    render_page_header(
        title="Vendor Management",
        subtitle="Organize supplier information, tax IDs, and vendor contacts efficiently.",
        icon="🏭"
    )
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
    render_page_header(
        title="Products & Services",
        subtitle="Manage inventory, services, and pricing with a clean product catalog.",
        icon="📦"
    )
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
    render_page_header(
        title="Tax Configuration",
        subtitle="Configure VAT, sales tax, and other rates for invoices and journal entries.",
        icon="⚖️"
    )
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
    render_page_header(
        title="Payment Methods",
        subtitle="Add and maintain payment options like cash, cards, and bank transfers.",
        icon="💳"
    )
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
    render_page_header(
        title="Invoices",
        subtitle="Create and review invoices with customer and employee assignment.",
        icon="🧾"
    )
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
    render_page_header(
        title="Journal Entries",
        subtitle="Build double-entry transactions with line items, invoices, vendors, and payment links.",
        icon="✍️"
    )

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
                        res = reverse_transaction(entry_to_del)
                        if res == "Success":
                            st.success("Journal Entry reversed and deleted!")
                            st.rerun()
                        else:
                            st.error(res)


# ── General Ledger ────────────────────────────────────────────────────────────

elif menu == "General Ledger":
    render_page_header(
        title="General Ledger",
        subtitle="Review journal item history, account flows, and ledger detail in one view.",
        icon="📖"
    )
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