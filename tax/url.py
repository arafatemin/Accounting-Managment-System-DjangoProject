from django.urls import path
from .views import *



urlpatterns = [
    path('tax/',TaxView.as_view(),name='tax')
]