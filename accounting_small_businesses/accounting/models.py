from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone


class Account(models.Model):
    ASSET, LIABILITY, EQUITY, INCOME, EXPENSE = ("AS", "LI", "EQ", "IN", "EX")
    TYPES = [
        (ASSET, "Asset"),
        (LIABILITY, "Liability"),
        (EQUITY, "Equity"),
        (INCOME, "Income"),
        (EXPENSE, "Expense"),
    ]
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=120)
    type = models.CharField(max_length=2, choices=TYPES)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        unique_together = [("org", "code")]

    def __str__(self):  # pragma: no cover
        return f"{self.code} {self.name}"


class FiscalYear(models.Model):
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    year = models.PositiveIntegerField()

    class Meta:
        unique_together = [("org", "year")]


class Period(models.Model):
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE)
    month = models.PositiveSmallIntegerField()  # 1..12
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = [("org", "fiscal_year", "month")]


class TaxRate(models.Model):
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    rate = models.DecimalField(max_digits=6, decimal_places=4)  # e.g. 0.2000
    inclusive = models.BooleanField(default=False)
    jurisdiction = models.CharField(max_length=40, blank=True, default="")


class JournalEntry(models.Model):
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    date = models.DateField()
    period = models.ForeignKey(Period, on_delete=models.PROTECT)
    posted_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=64, default="manual")
    reference = models.CharField(max_length=64, blank=True, default="")

    def clean(self):
        lines = list(self.lines.all())
        if not lines:
            raise ValidationError("Entry must have lines")
        debit = sum((l.debit or Decimal("0")) for l in lines)
        credit = sum((l.credit or Decimal("0")) for l in lines)
        if debit.quantize(Decimal("0.01")) != credit.quantize(Decimal("0.01")):
            raise ValidationError("Entry not balanced")
        if self.period.is_closed:
            raise ValidationError("Cannot post to closed period")

    def post(self, user):
        from core.models import AuditLog  # local import to avoid circular
        with transaction.atomic():
            self.full_clean()
            if self.posted_at:
                raise ValidationError("Already posted")
            # lock period row to avoid race on closing
            Period.objects.select_for_update().get(pk=self.period_id)
            if self.period.is_closed:
                raise ValidationError("Cannot post to closed period")
            self.posted_at = timezone.now()
            self.save(update_fields=["posted_at"])
            AuditLog.log(self.org, user, "journal.post", pk=self.pk, reference=self.reference)


class JournalLine(models.Model):
    entry = models.ForeignKey(JournalEntry, related_name="lines", on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    description = models.CharField(max_length=200, blank=True)
    debit = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    credit = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    def clean(self):
        d = self.debit or Decimal("0")
        c = self.credit or Decimal("0")
        if d and c:
            raise ValidationError("Line cannot have both debit and credit")
        if not (d or c):
            raise ValidationError("Line must have a debit or credit")
        if d < 0 or c < 0:
            raise ValidationError("Amounts must be non-negative")
from django.db import models

# Create your models here.
