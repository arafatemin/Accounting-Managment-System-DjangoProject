from django.urls import path
from .views import *

urlpatterns = [
    path('', StockView.as_view(), name='stock'),
    path('add',AddSotck.as_view(),name='add_stock'),
    path('<int:id>',single_stock,name='single_stock'),
    path('pdf/<int:id>', download_pdf, name='product_pdf'),
    path('edit_stock/<int:id>', edit_stock, name='edit_stock'),
]
