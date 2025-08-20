from decimal import Decimal
from django.db import models


class Item(models.Model):
    PRODUCT, SERVICE = ("product", "service")
    TYPES = [(PRODUCT, "Product"), (SERVICE, "Service")]
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    sku = models.CharField(max_length=40)
    name = models.CharField(max_length=120)
    type = models.CharField(max_length=10, choices=TYPES, default=PRODUCT)
    income_account = models.ForeignKey("accounting.Account", related_name="item_income", on_delete=models.PROTECT)
    inventory_account = models.ForeignKey("accounting.Account", related_name="item_inventory", on_delete=models.PROTECT, null=True, blank=True)
    cogs_account = models.ForeignKey("accounting.Account", related_name="item_cogs", on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        unique_together = [("org", "sku")]


class Warehouse(models.Model):
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=120)

    class Meta:
        unique_together = [("org", "code")]


class StockMove(models.Model):
    IN, OUT = ("in", "out")
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
    date = models.DateField()
    quantity = models.DecimalField(max_digits=14, decimal_places=4)
    direction = models.CharField(max_length=3, choices=[(IN, "In"), (OUT, "Out")])
    unit_cost = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)


class CostLayer(models.Model):
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=14, decimal_places=4)
    unit_cost = models.DecimalField(max_digits=18, decimal_places=4)
    remaining_qty = models.DecimalField(max_digits=14, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)


class COGSPosting(models.Model):
    org = models.ForeignKey("core.Organization", on_delete=models.CASCADE)
    stock_move = models.OneToOneField(StockMove, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    entry = models.ForeignKey("accounting.JournalEntry", on_delete=models.PROTECT)
from django.db import models

# Create your models here.
