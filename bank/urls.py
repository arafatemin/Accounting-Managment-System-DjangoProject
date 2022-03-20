from django.urls import path
from .views import *
from .income_views import *
from .outcome_views import *



urlpatterns = [
    path('',Banks.as_view(),name='banks'),
    path('transfer_money', TransferMoney.as_view(), name='transfer_money'),
    path('single_bank/<int:id>', single_bank, name='single_bank'),
    path('invoice_payments/<int:id>', invoice_payments, name='invoice_payments'),
    path('money_transfer_in/<int:id>', money_transfer_in, name='money_transfer_in'),
    path('org_debt_payment_in/<int:id>', org_debt_payment_in, name='org_debt_payment_in'),
    path('product_transfer_payment_in/<int:id>', product_transfer_payment_in, name='product_transfer_payment_in'),
    path('additional_income/<int:id>', additional_income, name='additional_income'),
    path('additional_outcome/<int:id>', additional_outcome, name='additional_outcome'),
]