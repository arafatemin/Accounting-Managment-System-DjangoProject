from django.urls import path
from .views import *



urlpatterns = [
    path('purchases/',PurchaseView.as_view(),name='purchase'),
    path('purchase/add/',AddPurchase.as_view(),name='add_purchase'),
    path('purchase/<int:id>',single_purchase,name='single_purchase'),
    path('pdf/<int:id>',download_pdf,name='purchase_pdf'),
    path('email/<int:id>/',send_email,name='purchase_email')
]