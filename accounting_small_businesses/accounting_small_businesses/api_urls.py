from django.urls import include, path
from rest_framework.routers import DefaultRouter
from core import views as core_views
from accounting import views as acc_views
from sales import views as sales_views

router = DefaultRouter()
router.register(r'organizations', core_views.OrganizationViewSet, basename='organization')
router.register(r'accounts', acc_views.AccountViewSet, basename='account')
router.register(r'customers', sales_views.CustomerViewSet, basename='customer')
router.register(r'invoices', sales_views.InvoiceViewSet, basename='invoice')
router.register(r'receipts', sales_views.ReceiptViewSet, basename='receipt')

urlpatterns = [
    path('', include(router.urls)),
]
