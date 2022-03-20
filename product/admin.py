from django.contrib import admin
from .models import Product,BaseProduct,ProductCategory,UnitType



admin.site.register(BaseProduct)
admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(UnitType)
