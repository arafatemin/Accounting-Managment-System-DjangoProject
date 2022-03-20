from django.urls import  path
from .views import *


urlpatterns = [
    path('vendors/',VendorView.as_view(),name='vendors'),
    path('vendors/<int:id>',single_vendor,name='single_vendor'),
    path('vendors/payment/<int:id>',make_payment,name='vendor_payment'),
    path('vendors/debt/<int:id>/',add_debt,name='add_debt')
]