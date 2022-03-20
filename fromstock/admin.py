from django.contrib import admin
from .models import ProductInStock,ProductWithUnit



admin.site.register(ProductWithUnit)
admin.site.register(ProductInStock)