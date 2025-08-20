from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Customer, Invoice, Receipt
from .serializers import CustomerSerializer, InvoiceSerializer, ReceiptSerializer
from .services import post_invoice, post_receipt
from accounting.models import Account


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by("id")
    serializer_class = CustomerSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().order_by("-id")
    serializer_class = InvoiceSerializer

    @action(detail=True, methods=["post"])
    def post_entry(self, request, pk=None):
        invoice = self.get_object()
        try:
            ar_id = int(request.data.get("ar_account"))
            tax_id = int(request.data.get("tax_account"))
            entry = post_invoice(invoice, ar_account=Account.objects.get(pk=ar_id), tax_account=Account.objects.get(pk=tax_id))
            return Response({"entry_id": entry.id, "posted_at": entry.posted_at}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all().order_by("-id")
    serializer_class = ReceiptSerializer

    @action(detail=True, methods=["post"])
    def post_entry(self, request, pk=None):
        receipt = self.get_object()
        try:
            bank_id = int(request.data.get("bank_account"))
            ar_id = int(request.data.get("ar_account"))
            entry = post_receipt(receipt, bank_account=Account.objects.get(pk=bank_id), ar_account=Account.objects.get(pk=ar_id))
            return Response({"entry_id": entry.id, "posted_at": entry.posted_at}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
