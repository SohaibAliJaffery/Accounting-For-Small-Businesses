from django.db import models


class BankAccount(models.Model):
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    account = models.ForeignKey("accounting.Account", on_delete=models.PROTECT)


class BankStatement(models.Model):
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()


class StatementLine(models.Model):
    statement = models.ForeignKey(BankStatement, related_name="lines", on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    matched_entry = models.ForeignKey("accounting.JournalEntry", null=True, blank=True, on_delete=models.SET_NULL)


class Reconciliation(models.Model):
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    as_of = models.DateField()
    balance_per_books = models.DecimalField(max_digits=18, decimal_places=2)
    balance_per_bank = models.DecimalField(max_digits=18, decimal_places=2)
from django.db import models

# Create your models here.
