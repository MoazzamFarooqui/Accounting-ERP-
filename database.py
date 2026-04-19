from sqlmodel import SQLModel, Field, create_engine as sql_create_engine, Session, select
from typing import List
import datetime as dt

# --- Database Setup ---

def get_engine():
    # pool_pre_ping helps maintain connection with MariaDB on Arch
    mysql_url = "mysql+mysqlconnector://root:moazzam123@localhost:3306/accounting_erp"
    return sql_create_engine(mysql_url, echo=False, pool_pre_ping=True)

engine = get_engine()

def init_db():
    SQLModel.metadata.create_all(engine)

# --- Models ---

# We use a constant for table args to keep code clean
TABLE_ARGS = {"extend_existing": True}

class AccountType(SQLModel, table=True):
    __tablename__ = "account_type"
    __table_args__ = TABLE_ARGS
    
    type_id: int | None = Field(default=None, primary_key=True)
    category_name: str

class Account(SQLModel, table=True):
    __tablename__ = "account"
    __table_args__ = TABLE_ARGS
    
    account_id: int = Field(primary_key=True)
    account_name: str
    account_code: str | None = Field(default=None)
    type_id: int = Field(foreign_key="account_type.type_id")
    balance: float = Field(default=0.0)

class Customer(SQLModel, table=True):
    __tablename__ = "customer"
    __table_args__ = TABLE_ARGS
    
    customer_id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str | None = Field(default=None)
    phone: str | None = Field(default=None)

class Employee(SQLModel, table=True):
    __tablename__ = "employee"
    __table_args__ = TABLE_ARGS
    
    employee_id: int | None = Field(default=None, primary_key=True)
    name: str
    role: str | None = Field(default=None)
    department: str | None = Field(default=None)
    hire_date: dt.date | None = Field(default=None)

class Invoice(SQLModel, table=True):
    __tablename__ = "invoice"
    __table_args__ = TABLE_ARGS
    
    invoice_id: int | None = Field(default=None, primary_key=True)
    date: dt.date | None = Field(default_factory=dt.date.today)
    total: float = Field(default=0.0)
    status: str | None = Field(default=None)
    customer_id: int = Field(foreign_key="customer.customer_id")
    employee_id: int = Field(foreign_key="employee.employee_id")

class Vendor(SQLModel, table=True):
    __tablename__ = "vendor"
    __table_args__ = TABLE_ARGS
    
    vendor_id: int | None = Field(default=None, primary_key=True)
    company_name: str
    contact: str | None = Field(default=None)
    tax_id: str | None = Field(default=None)

class Product(SQLModel, table=True):
    __tablename__ = "product"
    __table_args__ = TABLE_ARGS
    
    product_id: int | None = Field(default=None, primary_key=True)
    name: str
    unit_price: float = Field(default=0.0)
    category: str | None = Field(default=None)

class Tax(SQLModel, table=True):
    __tablename__ = "tax"
    __table_args__ = TABLE_ARGS
    
    tax_id: int | None = Field(default=None, primary_key=True)
    tax_name: str
    percentage: float = Field(default=0.0)

class PaymentMethod(SQLModel, table=True):
    __tablename__ = "payment_method"
    __table_args__ = TABLE_ARGS
    
    payment_id: int | None = Field(default=None, primary_key=True)
    method_name: str

class JournalEntry(SQLModel, table=True):
    __tablename__ = "journal_entry"
    __table_args__ = TABLE_ARGS
    
    entry_id: int | None = Field(default=None, primary_key=True)
    date: dt.datetime = Field(default_factory=dt.datetime.now)
    description: str | None = Field(default=None)
    status: str | None = Field(default=None)
    employee_id: int | None = Field(default=None, foreign_key="employee.employee_id")
    invoice_id: int | None = Field(default=None, foreign_key="invoice.invoice_id")
    vendor_id: int | None = Field(default=None, foreign_key="vendor.vendor_id")
    payment_id: int | None = Field(default=None, foreign_key="payment_method.payment_id")

class JournalItem(SQLModel, table=True):
    __tablename__ = "journal_item"
    __table_args__ = TABLE_ARGS
    
    entry_id: int = Field(foreign_key="journal_entry.entry_id", primary_key=True)
    line_no: int = Field(primary_key=True)
    debit: float = Field(default=0.0)
    credit: float = Field(default=0.0)
    account_id: int = Field(foreign_key="account.account_id")
    product_id: int | None = Field(default=None, foreign_key="product.product_id")
    tax_id: int | None = Field(default=None, foreign_key="tax.tax_id")

# --- Logic ---

def post_transaction(description: str, ledger_lines: List[dict], employee_id: int | None = None, 
                     invoice_id: int | None = None, vendor_id: int | None = None, 
                     payment_id: int | None = None, status: str = "Posted"):
    
    total_debit = sum(line.get("debit", 0.0) for line in ledger_lines)
    total_credit = sum(line.get("credit", 0.0) for line in ledger_lines)

    if abs(total_debit - total_credit) > 0.001:
        return f"Error: Transaction not balanced. Debit: {total_debit:.2f}, Credit: {total_credit:.2f}"

    with Session(engine) as session:
        try:
            new_entry = JournalEntry(
                description=description,
                status=status,
                employee_id=employee_id,
                invoice_id=invoice_id,
                vendor_id=vendor_id,
                payment_id=payment_id
            )
            session.add(new_entry)
            session.flush()

            for idx, line in enumerate(ledger_lines):
                item = JournalItem(
                    entry_id=new_entry.entry_id,
                    line_no=idx + 1,
                    account_id=line["account_id"],
                    debit=line.get("debit", 0.0),
                    credit=line.get("credit", 0.0),
                    product_id=line.get("product_id"),
                    tax_id=line.get("tax_id")
                )
                session.add(item)

                # Update account balance
                acc = session.get(Account, line["account_id"])
                if acc:
                    acc_type = session.get(AccountType, acc.type_id)
                    # Logic for Asset/Expense vs Liability/Equity/Revenue
                    if acc_type and acc_type.category_name in ["Asset", "Expense"]:
                        acc.balance += (item.debit - item.credit)
                    else:
                        acc.balance += (item.credit - item.debit)
            
            session.commit()
            return "Success"
        except Exception as e:
            session.rollback()
            return f"Error: {str(e)}"