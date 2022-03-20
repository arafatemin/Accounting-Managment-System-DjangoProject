from django.urls import path
from .views import *

urlpatterns = [
    path('', ReturnView.as_view(), name='return'),
    path('add',AddReturn.as_view(),name='add_return'),
    path('<int:id>',SingleReturn.as_view(),name='single_return'),
    path('pdf/<int:id>', download_pdf, name='return_pdf'),
]
