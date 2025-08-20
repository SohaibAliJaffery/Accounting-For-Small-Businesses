from rest_framework import viewsets
from .models import Organization
from .serializers import OrganizationSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all().order_by("id")
    serializer_class = OrganizationSerializer
from django.shortcuts import render

# Create your views here.
