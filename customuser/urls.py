from django.urls import path
from .views import single_customuser,CustomUserView


urlpatterns = [
    path('',CustomUserView.as_view(),name='customusers'),
    path('<int:id>',single_customuser,name='single_customuser')
]