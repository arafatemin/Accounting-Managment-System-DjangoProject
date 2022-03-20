from django.contrib import admin
from .models import *




admin.site.register(TransferPayment)
admin.site.register(ProductTransfer)
admin.site.register(TransferedProduct)
admin.site.register(OrgDebt)
admin.site.register(OrgDebtPayment)