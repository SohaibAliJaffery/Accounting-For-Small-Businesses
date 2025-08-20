from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError


class Customer(models.Model):
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True, default="")


class Invoice(models.Model):
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    date = models.DateField()
    due_date = models.DateField()
    posted_entry = models.ForeignKey("accounting.JournalEntry", null=True, blank=True, on_delete=models.SET_NULL)
    reference = models.CharField(max_length=64, blank=True, default="")

    @property
    def total(self) -> Decimal:
        return sum((l.total for l in self.lines.all()), Decimal("0"))


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="lines", on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    qty = models.DecimalField(max_digits=12, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    tax = models.ForeignKey("accounting.TaxRate", null=True, blank=True, on_delete=models.SET_NULL)
    income_account = models.ForeignKey("accounting.Account", on_delete=models.PROTECT)

    @property
    def subtotal(self) -> Decimal:
        return (self.qty or Decimal("0")) * (self.price or Decimal("0"))

    @property
    def tax_amount(self) -> Decimal:
        if not self.tax:
            return Decimal("0")
        rate = self.tax.rate or Decimal("0")
        if self.tax.inclusive:
            base = self.subtotal / (Decimal("1.0") + rate)
            return (self.subtotal - base).quantize(Decimal("0.01"))
        return (self.subtotal * rate).quantize(Decimal("0.01"))

    @property
    def total(self) -> Decimal:
        if self.tax and self.tax.inclusive:
            return self.subtotal
        return self.subtotal + self.tax_amount


class Receipt(models.Model):
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    posted_entry = models.ForeignKey("accounting.JournalEntry", null=True, blank=True, on_delete=models.SET_NULL)


class AROpenItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
from django.db import models

# Create your models here.
