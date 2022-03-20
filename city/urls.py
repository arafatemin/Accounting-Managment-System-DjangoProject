from django.urls import path
from .views import Cities



urlpatterns = [
    path('',Cities.as_view(),name='cities')
]