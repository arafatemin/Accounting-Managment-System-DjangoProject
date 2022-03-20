from django.urls import path
from .views import *



urlpatterns = [
    path('',TransferView.as_view(),name='transfer'),
    path('add/',AddTransfer.as_view(),name='add_transfer'),
    path('<int:id>',single_transfer,name='single_transfer'),
    path('pdf/<int:id>', download_pdf, name='transfer_pdf'),

]