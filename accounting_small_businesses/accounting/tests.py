from decimal import Decimal
from collections import defaultdict
from django.test import TestCase
from django.utils import timezone

from core.models import Organization
from accounting.models import Account, JournalLine
from sales.models import Customer, Invoice, InvoiceLine
from sales.services import post_invoice


class LedgerTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Org", code="ORG")
        # minimal COA
        self.ar = Account.objects.create(org=self.org, code="1100", name="AR", type=Account.ASSET)
        self.rev = Account.objects.create(org=self.org, code="4000", name="Revenue", type=Account.INCOME)
        self.tax = Account.objects.create(org=self.org, code="2100", name="VAT Payable", type=Account.LIABILITY)

    def test_invoice_posting_balances(self):
        cust = Customer.objects.create(org=self.org, name="Acme")
        inv = Invoice.objects.create(org=self.org, customer=cust, date=timezone.now().date(), due_date=timezone.now().date())
        InvoiceLine.objects.create(invoice=inv, description="Service", qty=1, price=Decimal("100.00"), income_account=self.rev)
        entry = post_invoice(inv, ar_account=self.ar, tax_account=self.tax)
        lines = list(entry.lines.all())
        debit = sum((l.debit or Decimal("0")) for l in lines)
        credit = sum((l.credit or Decimal("0")) for l in lines)
        assert debit == credit == Decimal("100.00")

    def test_trial_balance_equation(self):
        totals = defaultdict(Decimal)
        for line in JournalLine.objects.filter(entry__posted_at__isnull=False).select_related("account"):
            amt = (line.debit or Decimal("0")) - (line.credit or Decimal("0"))
            totals[line.account.type] += amt
        lhs = totals[Account.ASSET] - totals[Account.LIABILITY] - totals[Account.EQUITY] - totals[Account.INCOME] + totals[Account.EXPENSE]
        assert lhs.quantize(Decimal("0.01")) == Decimal("0.00")
from django.test import TestCase

# Create your tests here.
