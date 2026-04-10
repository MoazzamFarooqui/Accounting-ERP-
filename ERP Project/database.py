from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
import datetime as dt

# Connection String
mysql_url = "mysql+mysqlconnector://root:moazzam123@localhost:3306/accounting_erp"
engine = create_engine(mysql_url, echo=False)

class AccountType(SQLModel, table=True):
    __tablename__ = "account_type"
    type_id: Optional[int] = Field(default=None, primary_key=True)
    category_name: str

class Account(SQLModel, table=True):
    __tablename__ = "account"
    account_id: int = Field(primary_key=True)
    account_name: str
    account_code: Optional[str] = None
    type_id: int = Field(foreign_key="account_type.type_id")
    balance: float = Field(default=0.0)

class Customer(SQLModel, table=True):
    __tablename__ = "customer"
    customer_id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class Employee(SQLModel, table=True):
    __tablename__ = "employee"
    employee_id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: Optional[str] = None
    department: Optional[str] = None
    hire_date: Optional[dt.date] = None

class Invoice(SQLModel, table=True):
    __tablename__ = "invoice"
    invoice_id: Optional[int] = Field(default=None, primary_key=True)
    date: Optional[dt.date] = Field(default_factory=dt.date.today)
    total: float = Field(default=0.0)
    status: Optional[str] = None
    customer_id: int = Field(foreign_key="customer.customer_id")
    employee_id: int = Field(foreign_key="employee.employee_id")

class Vendor(SQLModel, table=True):
    __tablename__ = "vendor"
    vendor_id: Optional[int] = Field(default=None, primary_key=True)
    company_name: str
    contact: Optional[str] = None
    tax_id: Optional[str] = None

class Product(SQLModel, table=True):
    __tablename__ = "product"
    product_id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    unit_price: float = Field(default=0.0)
    category: Optional[str] = None

class Tax(SQLModel, table=True):
    __tablename__ = "tax"
    tax_id: Optional[int] = Field(default=None, primary_key=True)
    tax_name: str
    percentage: float = Field(default=0.0)

class PaymentMethod(SQLModel, table=True):
    __tablename__ = "payment_method"
    payment_id: Optional[int] = Field(default=None, primary_key=True)
    method_name: str

class JournalEntry(SQLModel, table=True):
    __tablename__ = "journal_entry"
    entry_id: Optional[int] = Field(default=None, primary_key=True)
    date: dt.datetime = Field(default_factory=dt.datetime.now)
    description: Optional[str] = None
    status: Optional[str] = None
    employee_id: Optional[int] = Field(default=None, foreign_key="employee.employee_id")
    invoice_id: Optional[int] = Field(default=None, foreign_key="invoice.invoice_id")
    vendor_id: Optional[int] = Field(default=None, foreign_key="vendor.vendor_id")
    payment_id: Optional[int] = Field(default=None, foreign_key="payment_method.payment_id")

class JournalItem(SQLModel, table=True):
    __tablename__ = "journal_item"
    entry_id: int = Field(foreign_key="journal_entry.entry_id", primary_key=True)
    line_no: int = Field(primary_key=True)
    debit: float = Field(default=0.0)
    credit: float = Field(default=0.0)
    account_id: int = Field(foreign_key="account.account_id")
    product_id: Optional[int] = Field(default=None, foreign_key="product.product_id")
    tax_id: Optional[int] = Field(default=None, foreign_key="tax.tax_id")

def init_db():
    SQLModel.metadata.create_all(engine)

def post_transaction(description: str, ledger_lines: List[dict], employee_id: Optional[int] = None, 
                     invoice_id: Optional[int] = None, vendor_id: Optional[int] = None, 
                     payment_id: Optional[int] = None, status: str = "Posted"):
    
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
                    if acc_type and acc_type.category_name in ["Asset", "Expense"]:
                        acc.balance += (item.debit - item.credit)
                    else:
                        acc.balance += (item.credit - item.debit)
            
            session.commit()
            return "Success"
        except Exception as e:
            session.rollback()
            return f"Error: {str(e)}"
