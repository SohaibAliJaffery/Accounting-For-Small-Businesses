from decimal import Decimal
from django.db import models


class Vendor(models.Model):
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True, default="")


class Bill(models.Model):
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    date = models.DateField()
    due_date = models.DateField()
    posted_entry = models.ForeignKey("accounting.JournalEntry", null=True, blank=True, on_delete=models.SET_NULL)


class BillLine(models.Model):
    bill = models.ForeignKey(Bill, related_name="lines", on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    qty = models.DecimalField(max_digits=12, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    tax = models.ForeignKey("accounting.TaxRate", null=True, blank=True, on_delete=models.SET_NULL)
    expense_account = models.ForeignKey("accounting.Account", on_delete=models.PROTECT)

    @property
    def subtotal(self) -> Decimal:
        return (self.qty or Decimal("0")) * (self.price or Decimal("0"))


class Payment(models.Model):
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    posted_entry = models.ForeignKey("accounting.JournalEntry", null=True, blank=True, on_delete=models.SET_NULL)


class APOpenItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
from django.db import models

# Create your models here.
