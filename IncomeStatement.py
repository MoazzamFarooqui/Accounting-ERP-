from fpdf import FPDF
from datetime import datetime
import pandas as pd


class IncomeStatementPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")


def generate_income_statement_pdf(df_accounts, entity_name="Company", period_date=None):
    """
    Income Statement — sign convention
    ====================================
    REVENUE  accounts  → use balance as-is  (credit-normal, positive = good)
    EXPENSE  accounts  → use abs(balance)   (debit-normal,  always positive)
    ASSET    accounts  → use balance as-is  (for closing stock)

    Structure:
        Revenue
      - Cost of Sales  (Opening Inv + Purchases - Closing Stock)
      = Gross Profit
      - Operating Expenses
      = Operating Profit / Operating Loss
      + Other Income
      = Net Profit / Net Loss
    """

    if period_date is None:
        period_date = datetime.now().strftime("%b %d, %Y").upper()

    df = df_accounts.copy()
    for col in ("type", "account_name", "balance"):
        if col not in df.columns:
            raise ValueError(f"df_accounts must contain column '{col}'")

    df["type_upper"] = df["type"].fillna("").str.strip().str.upper()
    df["name_upper"] = df["account_name"].fillna("").str.strip().str.upper()

    # ── REVENUE ────────────────────────────────────────────────────────────
    REVENUE_TYPES = {"REVENUE", "INCOME", "SALES", "SALE"}
    revenue_df = df[df["type_upper"].isin(REVENUE_TYPES)].copy()
    total_revenue = revenue_df["balance"].sum()

    # ── COGS detection ─────────────────────────────────────────────────────
    COGS_TYPE_KEYWORDS = {"COGS", "COST OF SALES", "COST OF GOODS", "PURCHASES"}
    COGS_NAME_KEYWORDS = ("PURCHASE", "COST OF GOOD", "COGS", "INVENTORY COST",
                          "DIRECT MATERIAL", "DIRECT LABOUR", "DIRECT LABOR",
                          "FREIGHT IN", "CLOSING STOCK", "OPENING STOCK",
                          "BEGINNING INVENTORY", "ENDING INVENTORY")

    cogs_by_type = df["type_upper"].isin(COGS_TYPE_KEYWORDS)
    cogs_by_name = (
        df["name_upper"].apply(lambda n: any(kw in n for kw in COGS_NAME_KEYWORDS)) &
        (df["type_upper"] == "EXPENSE")
    )
    cogs_df  = df[cogs_by_type | cogs_by_name].copy()
    cogs_ids = set(cogs_df.index)

    opening_inv_df = cogs_df[cogs_df["name_upper"].str.contains("OPENING|BEGINNING", na=False)]
    closing_inv_df = cogs_df[cogs_df["name_upper"].str.contains("CLOSING|ENDING",    na=False)]
    purchase_df    = cogs_df[
        ~cogs_df.index.isin(opening_inv_df.index) &
        ~cogs_df.index.isin(closing_inv_df.index)
    ]

    opening_inventory = abs(opening_inv_df["balance"].sum())
    total_purchases   = abs(purchase_df["balance"].sum())
    closing_stock     = abs(closing_inv_df["balance"].sum())

    if closing_stock == 0:
        inv_asset_df  = df[
            df["name_upper"].str.contains("INVENTORY|STOCK", na=False) &
            (df["type_upper"] == "ASSET")
        ]
        closing_stock = abs(inv_asset_df["balance"].sum())

    goods_available = opening_inventory + total_purchases
    cost_of_sales   = goods_available - closing_stock
    gross_profit    = total_revenue - cost_of_sales

    # ── OPERATING EXPENSES ─────────────────────────────────────────────────
    op_exp_df = df[
        (df["type_upper"] == "EXPENSE") &
        (~df.index.isin(cogs_ids))
    ].copy()
    op_exp_df["display_balance"] = op_exp_df["balance"].abs()
    total_op_expenses = op_exp_df["display_balance"].sum()
    operating_income  = gross_profit - total_op_expenses

    # ── OTHER INCOME ───────────────────────────────────────────────────────
    OTHER_INCOME_TYPES = {"OTHER INCOME", "NON-OPERATING INCOME",
                          "INTEREST INCOME", "DIVIDEND INCOME", "GAIN"}
    other_income_df    = df[df["type_upper"].isin(OTHER_INCOME_TYPES)].copy()
    total_other_income = other_income_df["balance"].sum()

    net_income = operating_income + total_other_income

    # ── PDF helpers ────────────────────────────────────────────────────────
    pdf    = IncomeStatementPDF()
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
    pdf.cell(0, 7, "INCOME STATEMENT", 0, 1, "C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"For the Period Ended {period_date}", 0, 1, "C")
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

    # ── REVENUE ─────────────────────────────────────────────────────────────
    row("REVENUE", bold=True, underline=True)
    if revenue_df.empty:
        row("  (No revenue accounts found)", c1="-")
    else:
        for _, r in revenue_df.iterrows():
            row(f"  {r['account_name']}", c1=money(r["balance"]))
    divider()
    section_total("Total Revenue", total_revenue, is_cost=False)
    pdf.ln(3)

    # ── COST OF SALES ────────────────────────────────────────────────────────
    row("COST OF SALES", bold=True, underline=True)
    row("  Opening Inventory",           c2=money(opening_inventory))
    if not purchase_df.empty:
        for _, r in purchase_df.iterrows():
            row(f"  {r['account_name']}", c2=money(abs(r["balance"])))
    else:
        row("  Purchases / Direct Costs", c2=money(total_purchases))
    row("  Goods Available for Sale",    c2=money(goods_available))
    row("  Less: Closing Stock",         c2=cost(closing_stock))
    divider()
    section_total("Total Cost of Sales", cost_of_sales, is_cost=True)
    pdf.ln(3)

    # ── GROSS PROFIT / GROSS LOSS ───────────────────────────────────────────
    gross_label = "GROSS PROFIT" if gross_profit >= 0 else "GROSS LOSS"
    highlight_row(gross_label, gross_profit)
    pdf.ln(4)

    # ── OPERATING EXPENSES ───────────────────────────────────────────────────
    row("OPERATING EXPENSES", bold=True, underline=True)
    if op_exp_df.empty:
        row("  (No operating expense accounts found)", c2="-")
    else:
        for _, r in op_exp_df.iterrows():
            row(f"  {r['account_name']}", c2=money(r["display_balance"]))
    divider()
    section_total("Total Operating Expenses", total_op_expenses, is_cost=True)
    pdf.ln(3)

    # ── OPERATING PROFIT / OPERATING LOSS ───────────────────────────────────
    op_label = "OPERATING PROFIT" if operating_income >= 0 else "OPERATING LOSS"
    highlight_row(op_label, operating_income)
    pdf.ln(4)

    # ── OTHER INCOME ─────────────────────────────────────────────────────────
    if not other_income_df.empty or total_other_income != 0:
        row("OTHER INCOME", bold=True, underline=True)
        for _, r in other_income_df.iterrows():
            row(f"  {r['account_name']}", c2=money(r["balance"]))
        divider()
        section_total("Total Other Income", total_other_income, is_cost=False)
        pdf.ln(3)

    # ── NET PROFIT / NET LOSS ────────────────────────────────────────────────
    is_profit   = net_income >= 0
    final_label = "NET PROFIT" if is_profit else "NET LOSS"
    color       = (150, 210, 150) if is_profit else (230, 150, 150)
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(*color)
    pdf.set_draw_color(0, 0, 0)
    pdf.cell(C0 + C1 + C2, 10, final_label, 1, 0, "L", True)
    pdf.cell(C3, 10, money(abs(net_income)), 1, 0, "R", True)
    pdf.ln()
    pdf.set_fill_color(255, 255, 255)
    pdf.ln(6)

    # ── SUMMARY BOX ──────────────────────────────────────────────────────────
    op_summary_label    = "Operating Profit" if operating_income >= 0 else "Operating Loss"
    gross_summary_label = "Gross Profit"     if gross_profit     >= 0 else "Gross Loss"
    net_summary_label   = "Net Profit"       if net_income       >= 0 else "Net Loss"

    pdf.set_fill_color(245, 245, 245)
    summary_items = [
        ("Total Revenue",       money(total_revenue)),
        ("Cost of Sales",       cost(cost_of_sales)),
        (gross_summary_label,   money(abs(gross_profit))),
        ("Operating Expenses",  cost(total_op_expenses)),
        (op_summary_label,      money(abs(operating_income))),
        ("Other Income",        money(total_other_income)),
        (net_summary_label,     money(abs(net_income))),
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