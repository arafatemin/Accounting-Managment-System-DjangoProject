from django.template import Library
from product.models import Product
from django.shortcuts import reverse
from product.templatetags.product import cpu
from invoice.models import Payment as InvoicePayment
from additional.models import AdditionalIncomes, AdditionalOutcomes
from bank.models import *
from purchase.models import Payment as PurchasePayment
from purchase.models import DebtPayment
from product_transfer.models import *
from django import template
from returnproduct.models import ReturnPayment

register = template.Library()


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def accountIncome(account):
    income = 0
    for i in InvoicePayment.objects.filter(bank=account): income += i.amount
    for i in Transfer.objects.filter(to_account=account): income += i.amount
    for i in OrgDebtPayment.objects.filter(to_bank=account): income += i.amount
    for i in TransferPayment.objects.filter(to_bank=account): income += i.amount
    for i in AdditionalIncomes.objects.filter(bank=account):income += i.amount

    return income

@register.filter
def accountOutcome(account):
    outcome = 0
    for i in PurchasePayment.objects.filter(bank=account): outcome += i.amount
    for i in Transfer.objects.filter(from_account=account): outcome += i.amount
    for i in OrgDebtPayment.objects.filter(from_bank=account): outcome += i.amount
    for i in TransferPayment.objects.filter(from_bank=account): outcome += i.amount
    for i in DebtPayment.objects.filter(bank=account): outcome += i.amount
    for i in ReturnPayment.objects.filter(bank=account): outcome += i.amount
    for i in AdditionalOutcomes.objects.filter(bank=account):outcome +=i.amount
    return outcome


@register.filter
def outcomeCategory(category,account):
    outcome = 0
    for i in AdditionalOutcomes.objects.filter(category=category,bank=account):outcome +=i.amount
    return outcome

