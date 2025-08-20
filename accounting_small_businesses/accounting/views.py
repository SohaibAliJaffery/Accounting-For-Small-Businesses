from rest_framework import viewsets
from .models import Account
from .serializers import AccountSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all().order_by("code")
    serializer_class = AccountSerializer
from django.shortcuts import render

# Create your views here.
