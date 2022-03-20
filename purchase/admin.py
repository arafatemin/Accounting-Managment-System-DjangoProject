from django.contrib import admin
from .models import *



admin.site.register(BoughtProduct)
# admin.site.register(ReturnedProduct)
admin.site.register(Payment)
admin.site.register(Purchase)