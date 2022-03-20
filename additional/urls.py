from django.urls import path
from .views import *


urlpatterns = [
    path('outcome',OutcomeView.as_view(),name='outcome'),
    path('outcome/cateogry',OutcomeCategoryView.as_view(),name='outcome_category'),
    path('income/cateogry',IncomeCategoryView.as_view(),name='income_category'),
    path('incomes',IncomeView.as_view(),name='income')
]