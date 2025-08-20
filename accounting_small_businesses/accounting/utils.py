from datetime import date as date_type
from django.db import transaction

from .models import FiscalYear, Period


@transaction.atomic
def get_or_create_period(org, d):
    if isinstance(d, date_type):
        year = d.year
        month = d.month
    else:
        year = d.year
        month = d.month
    fy, _ = FiscalYear.objects.get_or_create(org=org, year=year)
    period, _ = Period.objects.get_or_create(org=org, fiscal_year=fy, month=month)
    return period
