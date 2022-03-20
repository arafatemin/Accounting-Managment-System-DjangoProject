from django.urls import path
from .views import *

urlpatterns = [
    path('income',IncomeReport.as_view(),name='by_income'),
    path('outcome',outcome_report,name='by_outcome'),
    path('balance_sheet',balance_sheet,name='balance_sheet'),
    path('product_report',product_report,name='product_report'),
    path('general_report',general_report,name='general_report'),
    path('organization',by_organization,name='org_report'),
    path('single_org_report/<int:id>',single_org_report,name='single_org_report')
]