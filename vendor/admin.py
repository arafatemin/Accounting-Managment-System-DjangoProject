from django.contrib import admin
from .models import *
from purchase.models import Debt,DebtPayment

admin.site.register(Vendor)
admin.site.register(Debt)
admin.site.register(DebtPayment)
