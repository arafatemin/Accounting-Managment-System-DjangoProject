from django.urls import path
from .views import *


urlpatterns = [
    path('',organizations,name='organizations'),
    path('add',AddOrganization.as_view(),name='add_organizations'),
    path('org/add_debt/<int:id>/', add_debt, name='add_org_debt'),
    path('<int:id>',single_organization,name='single_organization'),
    path('<int:id>/', make_payment, name='org_make_payment'),

]