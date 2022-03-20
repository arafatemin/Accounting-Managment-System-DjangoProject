from django.urls import path
from .views import single_customer,CustomerView,make_payment,update_customer



urlpatterns = [
    path('',CustomerView.as_view(),name='customers'),
    path('single_customer/<int:id>',single_customer,name='single_customer'),
    path('make_payment/<int:id>',make_payment,name='customer_payment'),
    path('update_customer/<int:id>',update_customer,name='update_customer'),
]