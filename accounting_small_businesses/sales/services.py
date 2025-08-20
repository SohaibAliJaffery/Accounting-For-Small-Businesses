from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from accounting.models import Account, JournalEntry, JournalLine
from accounting.utils import get_or_create_period


@transaction.atomic
def post_invoice(invoice, ar_account: Account, tax_account: Account):
    if invoice.posted_entry_id:
        raise ValidationError("Invoice already posted")
    period = get_or_create_period(invoice.org, invoice.date)

    entry = JournalEntry.objects.create(
        org=invoice.org, date=invoice.date, period=period, source="sales.invoice", reference=str(invoice.pk)
    )

    total_tax = Decimal("0")
    revenue_total = Decimal("0")
    for line in invoice.lines.select_related("tax", "income_account"):
        revenue_total += line.subtotal
        tax_amt = line.tax_amount
        total_tax += tax_amt
        # Credit revenue
        JournalLine.objects.create(entry=entry, account=line.income_account, credit=line.subtotal)
        # Credit tax if exclusive
        if line.tax and not line.tax.inclusive and tax_amt:
            JournalLine.objects.create(entry=entry, account=tax_account, credit=tax_amt)

    ar_total = revenue_total + (total_tax if total_tax else Decimal("0"))
    JournalLine.objects.create(entry=entry, account=ar_account, debit=ar_total)

    entry.post(user=None)
    invoice.posted_entry = entry
    invoice.save(update_fields=["posted_entry"])
    return entry


@transaction.atomic
def post_receipt(receipt, bank_account: Account, ar_account: Account):
    if receipt.posted_entry_id:
        raise ValidationError("Receipt already posted")
    period = get_or_create_period(receipt.org, receipt.date)
    entry = JournalEntry.objects.create(
        org=receipt.org, date=receipt.date, period=period, source="sales.receipt", reference=str(receipt.pk)
    )
    JournalLine.objects.create(entry=entry, account=bank_account, debit=receipt.amount)
    JournalLine.objects.create(entry=entry, account=ar_account, credit=receipt.amount)
    entry.post(user=None)
    receipt.posted_entry = entry
    receipt.save(update_fields=["posted_entry"])
    return entry
