"""Double-entry bookkeeping engine following SKR03 conventions.

Creates balanced journal entries (Buchungssätze) where debits always equal credits.
"""

from pydantic import BaseModel
from datetime import date


class JournalLine(BaseModel):
    account: str
    account_name: str
    debit: float
    credit: float


class BookingEntry(BaseModel):
    date: str
    description: str
    lines: list[JournalLine]
    balanced: bool
    total_debit: float
    total_credit: float


# Standard SKR03 accounts for booking
BANK_ACCOUNT = "1200"  # Bank (asset account)
VORSTEUER_ACCOUNT = "1576"  # Vorsteuer 19% (input VAT receivable)
VORSTEUER_7_ACCOUNT = "1571"  # Vorsteuer 7% (input VAT receivable, reduced)

ACCOUNT_NAMES: dict[str, str] = {
    "1200": "Bank",
    "1576": "Abziehbare Vorsteuer 19%",
    "1571": "Abziehbare Vorsteuer 7%",
}


def create_booking_entry(
    transaction_date: str,
    description: str,
    expense_account: str,
    expense_account_name: str,
    gross_amount: float,
    net_amount: float,
    vat_amount: float,
    vat_rate: float,
) -> BookingEntry:
    """Create a double-entry booking record (Buchungssatz).

    Standard expense booking pattern:
        Debit: Expense account (net amount)
        Debit: Vorsteuer account (VAT amount)
        Credit: Bank account (gross amount)

    This ensures: total debits = total credits (balanced).

    Args:
        transaction_date: YYYY-MM-DD format
        description: Booking text (Buchungstext)
        expense_account: SKR03 expense account code
        expense_account_name: Human-readable account name
        gross_amount: Total amount paid (incl. VAT)
        net_amount: Amount excl. VAT
        vat_amount: VAT portion
        vat_rate: VAT rate applied (0.19, 0.07, 0.0)
    """
    lines: list[JournalLine] = []

    # Debit: Expense account (net amount)
    lines.append(JournalLine(
        account=expense_account,
        account_name=expense_account_name,
        debit=net_amount,
        credit=0.0,
    ))

    # Debit: Vorsteuer (input VAT) if applicable
    if vat_amount > 0:
        vorsteuer_acct = VORSTEUER_7_ACCOUNT if vat_rate <= 0.07 else VORSTEUER_ACCOUNT
        vorsteuer_name = ACCOUNT_NAMES.get(vorsteuer_acct, "Vorsteuer")
        lines.append(JournalLine(
            account=vorsteuer_acct,
            account_name=vorsteuer_name,
            debit=vat_amount,
            credit=0.0,
        ))

    # Credit: Bank account (gross amount)
    lines.append(JournalLine(
        account=BANK_ACCOUNT,
        account_name=ACCOUNT_NAMES[BANK_ACCOUNT],
        debit=0.0,
        credit=gross_amount,
    ))

    total_debit = round(sum(line.debit for line in lines), 2)
    total_credit = round(sum(line.credit for line in lines), 2)
    balanced = abs(total_debit - total_credit) < 0.01  # floating point tolerance

    return BookingEntry(
        date=transaction_date,
        description=description,
        lines=lines,
        balanced=balanced,
        total_debit=total_debit,
        total_credit=total_credit,
    )
