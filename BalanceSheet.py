from fpdf import FPDF
from datetime import datetime
import pandas as pd


class BalanceSheetPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")


def _normalize_accounts(df_accounts):
    required_cols = ("type", "account_name", "balance")
    for col in required_cols:
        if col not in df_accounts.columns:
            raise ValueError(f"df_accounts must contain column '{col}'")

    df = df_accounts.copy()
    df["type_upper"] = df["type"].fillna("").astype(str).str.strip().str.upper()
    df["account_name"] = df["account_name"].fillna("").astype(str)
    df["balance"] = pd.to_numeric(df["balance"], errors="coerce").fillna(0.0)
    return df


def _is_revenue_type(type_value: str) -> bool:
    revenue_types = {
        "REVENUE", "INCOME", "SALES", "SALE",
        "OTHER INCOME", "NON-OPERATING INCOME",
        "INTEREST INCOME", "DIVIDEND INCOME", "GAIN"
    }
    return type_value in revenue_types or "REVENUE" in type_value


def _is_expense_type(type_value: str) -> bool:
    expense_types = {
        "EXPENSE", "COGS", "COST OF SALES",
        "COST OF GOODS", "PURCHASES"
    }
    return (
        type_value in expense_types or
        "EXPENSE" in type_value or
        type_value.startswith("COST ")
    )


def prepare_balance_sheet_data(df_accounts):
    df = _normalize_accounts(df_accounts)

    assets_df = df[df["type_upper"].str.contains("ASSET", na=False)].copy()
    liabilities_df = df[df["type_upper"].str.contains("LIABILITY", na=False)].copy()
    equity_df = df[
        df["type_upper"].str.contains("EQUITY|CAPITAL|RETAINED", regex=True, na=False)
    ].copy()

    revenue_df = df[df["type_upper"].apply(_is_revenue_type)].copy()
    expense_df = df[df["type_upper"].apply(_is_expense_type)].copy()

    total_assets = float(assets_df["balance"].sum())
    total_liabilities = float(abs(liabilities_df["balance"].sum()))
    base_equity_total = float(abs(equity_df["balance"].sum()))
    current_earnings = float(abs(revenue_df["balance"].sum()) - expense_df["balance"].sum())
    total_equity = float(base_equity_total + current_earnings)
    liabilities_and_equity_total = float(total_liabilities + total_equity)
    difference = float(total_assets - liabilities_and_equity_total)

    return {
        "assets_df": assets_df,
        "liabilities_df": liabilities_df,
        "equity_df": equity_df,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "base_equity_total": base_equity_total,
        "current_earnings": current_earnings,
        "total_equity": total_equity,
        "liabilities_and_equity_total": liabilities_and_equity_total,
        "difference": difference,
    }


def generate_balance_sheet_pdf(df_accounts, entity_name="Company", as_of_date=None):
    if as_of_date is None:
        as_of_date = datetime.now().strftime("%b %d, %Y").upper()

    bs = prepare_balance_sheet_data(df_accounts)

    pdf = BalanceSheetPDF()
    pdf.add_page()
    PAGE_W = pdf.w - 2 * pdf.l_margin
    C0 = PAGE_W * 0.45
    C1 = PAGE_W * 0.18
    C2 = PAGE_W * 0.18
    C3 = PAGE_W * 0.19

    def money(val):
        if round(val, 2) == 0:
            return "-"
        if val < 0:
            return f"({abs(val):,.2f})"
        return f"{val:,.2f}"

    def cost(val):
        if round(val, 2) == 0:
            return "-"
        return f"({abs(val):,.2f})"

    def row(label, c1="", c2="", c3="", bold=False, underline=False,
            border=0, fill=False):
        style = ""
        if bold and underline:
            style = "BU"
        elif bold:
            style = "B"
        elif underline:
            style = "U"
        pdf.set_font("Arial", style, 10)
        if fill:
            pdf.set_fill_color(230, 230, 230)
        pdf.cell(C0, 7, label, border, 0, "L", fill)
        pdf.set_font("Arial", "B" if bold else "", 10)
        pdf.cell(C1, 7, c1, border, 0, "R", fill)
        pdf.cell(C2, 7, c2, border, 0, "R", fill)
        pdf.cell(C3, 7, c3, border, 0, "R", fill)
        pdf.ln()
        if fill:
            pdf.set_fill_color(255, 255, 255)

    def divider():
        pdf.set_draw_color(180, 180, 180)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + PAGE_W, pdf.get_y())
        pdf.ln(1)

    def section_total(label, val, is_cost=False):
        row(label, c3=cost(val) if is_cost else money(val), bold=True, fill=True)

    def highlight_row(label, val, size=11, positive_color=(200, 230, 200)):
        color = positive_color if val >= 0 else (255, 200, 200)
        pdf.set_font("Arial", "B", size)
        pdf.set_fill_color(*color)
        pdf.cell(C0 + C1 + C2, 9, label, 1, 0, "L", True)
        pdf.cell(C3, 9, money(abs(val)), 1, 0, "R", True)
        pdf.ln()
        pdf.set_fill_color(255, 255, 255)

    # ── TITLE ───────────────────────────────────────────────────────────────
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, entity_name, 0, 1, "C")
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, "BALANCE SHEET", 0, 1, "C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"As of {as_of_date}", 0, 1, "C")
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, "C")
    pdf.ln(4)

    # ── COLUMN HEADERS ──────────────────────────────────────────────────────
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(50, 50, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(C0, 8, "Description",   0, 0, "L", True)
    pdf.cell(C1, 8, "Detail ($)",    0, 0, "R", True)
    pdf.cell(C2, 8, "Sub-Total ($)", 0, 0, "R", True)
    pdf.cell(C3, 8, "Total ($)",     0, 0, "R", True)
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

    # ── ASSETS ─────────────────────────────────────────────────────────────
    row("ASSETS", bold=True, underline=True)
    if bs["assets_df"].empty:
        row("  (No asset accounts found)", c1="-")
    else:
        for _, r in bs["assets_df"].sort_values("account_name").iterrows():
            row(f"  {r['account_name']}", c1=money(r["balance"]))
    divider()
    section_total("Total Assets", bs["total_assets"], is_cost=False)
    pdf.ln(3)

    # ── LIABILITIES ────────────────────────────────────────────────────────
    row("LIABILITIES", bold=True, underline=True)
    if bs["liabilities_df"].empty:
        row("  (No liability accounts found)", c1="-")
    else:
        for _, r in bs["liabilities_df"].sort_values("account_name").iterrows():
            row(f"  {r['account_name']}", c1=money(abs(r["balance"])))
    divider()
    section_total("Total Liabilities", bs["total_liabilities"], is_cost=False)
    pdf.ln(3)

    # ── EQUITY ─────────────────────────────────────────────────────────────
    row("EQUITY", bold=True, underline=True)
    if bs["equity_df"].empty:
        row("  (No equity accounts found)", c1="-")
    else:
        for _, r in bs["equity_df"].sort_values("account_name").iterrows():
            row(f"  {r['account_name']}", c1=money(abs(r["balance"])))
    row("  Current Year Earnings", c2=money(bs["current_earnings"]))
    divider()
    section_total("Total Equity", bs["total_equity"], is_cost=False)
    pdf.ln(3)

    # ── TOTAL LIABILITIES AND EQUITY ───────────────────────────────────────
    row("Total Liabilities + Equity", c3=money(bs["liabilities_and_equity_total"]), bold=True, fill=True)
    pdf.ln(3)

    # ── BALANCE CHECK ───────────────────────────────────────────────────────
    if abs(bs["difference"]) <= 0.01:
        highlight_row("BALANCED", bs["total_assets"], positive_color=(200, 230, 200))
    else:
        highlight_row("OUT OF BALANCE", bs["difference"], positive_color=(255, 200, 200))
    pdf.ln(4)

    # ── SUMMARY BOX ──────────────────────────────────────────────────────────
    pdf.set_fill_color(245, 245, 245)
    summary_items = [
        ("Total Assets",         money(bs["total_assets"])),
        ("Total Liabilities",    money(bs["total_liabilities"])),
        ("Base Equity",          money(bs["base_equity_total"])),
        ("Current Earnings",     money(bs["current_earnings"])),
        ("Total Equity",         money(bs["total_equity"])),
        ("Liabilities + Equity", money(bs["liabilities_and_equity_total"])),
        ("Difference",           money(bs["difference"])),
    ]
    box_w   = PAGE_W * 0.5
    x_start = pdf.l_margin + PAGE_W - box_w
    pdf.set_x(x_start)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(box_w, 7, "  SUMMARY", 1, 1, "L", True)
    for label, val in summary_items:
        pdf.set_x(x_start)
        pdf.set_font("Arial", "", 9)
        pdf.cell(box_w * 0.6, 6, f"  {label}", 1, 0, "L")
        pdf.set_font("Arial", "B", 9)
        pdf.cell(box_w * 0.4, 6, val, 1, 1, "R")

    output = pdf.output(dest="S")
    if isinstance(output, str):
        return output.encode("latin-1")
    return bytes(output)
