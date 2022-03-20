from django.contrib import admin
from .models import Invoice,Payment,SoldProduct,ReturnedProduct






admin.site.register(Invoice)
admin.site.register(Payment)
admin.site.register(SoldProduct)
# admin.site.register(ReturnedProduct)
