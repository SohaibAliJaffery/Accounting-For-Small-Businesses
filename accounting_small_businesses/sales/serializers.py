from rest_framework import serializers
from .models import Customer, Invoice, InvoiceLine, Receipt


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "org", "name", "email"]


class InvoiceLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLine
        fields = ["id", "description", "qty", "price", "tax", "income_account"]


class InvoiceSerializer(serializers.ModelSerializer):
    lines = InvoiceLineSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ["id", "org", "customer", "date", "due_date", "reference", "posted_entry", "lines"]
        read_only_fields = ["posted_entry"]

    def create(self, validated_data):
        lines = validated_data.pop("lines", [])
        invoice = super().create(validated_data)
        for line in lines:
            InvoiceLine.objects.create(invoice=invoice, **line)
        return invoice


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ["id", "org", "customer", "date", "amount", "posted_entry"]
        read_only_fields = ["posted_entry"]
