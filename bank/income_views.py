from django.shortcuts import render, get_object_or_404, redirect, reverse
from customuser.models import CustomUser
from django.views import View
from django.forms import ModelForm
from .models import *
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from product.models import Product
from product.templatetags.product import cpu
from invoice.models import Payment as InvoicePayment
from additional.models import AdditionalIncomes, AdditionalOutcomes
from bank.models import *
from purchase.models import Payment as PurchasePayment
from purchase.models import DebtPayment
from purchase.models import DebtPayment
from product_transfer.models import *
from returnproduct.models import ReturnPayment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime


def invoice_payments(request, id):
    account = get_object_or_404(Bank, id=id)
    current_org = get_object_or_404(CustomUser, username=request.user.username).organization
    payments = InvoicePayment.objects.filter(bank=account).order_by("-id")

    context = {}

    if 'from' in request.GET:
        time = request.GET['from'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            payments = payments.filter(date__gte=t)
            context['from'] = request.GET['from']

        # time = datetime()

    if 'to' in request.GET:
        time = request.GET['to'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            payments = payments.filter(date__lte=t)
            context['to'] = request.GET['to']

    p = Paginator(payments, 30)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)

    index = page_obj.number - 1
    max_index = len(p.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = list(p.page_range)[start_index:end_index]
    total_pages = p.num_pages

    total = 0
    for p in payments:
        total += p.amount

    context = {
        'payments': payments,
        'account': account,
        'page_obj': page_obj,
        'page_range': page_range,
        'total_pages': total_pages,
        'total': total,
    }

    return render(request, 'incomes/invoice_payments.html', context=context)


def money_transfer_in(request, id):
    account = get_object_or_404(Bank, id=id)
    current_org = get_object_or_404(CustomUser, username=request.user.username).organization
    money_transfer_in = Transfer.objects.filter(to_account=account).order_by("-id")

    context = {}

    if 'from' in request.GET:
        time = request.GET['from'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            money_transfer_in = money_transfer_in.filter(date__gte=t)
            context['from'] = request.GET['from']

        # time = datetime()

    if 'to' in request.GET:
        time = request.GET['to'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            money_transfer_in = money_transfer_in.filter(date__lte=t)
            context['to'] = request.GET['to']

    p = Paginator(money_transfer_in, 30)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)

    index = page_obj.number - 1
    max_index = len(p.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = list(p.page_range)[start_index:end_index]
    total_pages = p.num_pages

    total = 0
    for p in money_transfer_in:
        total += p.amount

    context = {
        'payments': money_transfer_in,
        'account': account,
        'page_obj': page_obj,
        'page_range': page_range,
        'total_pages': total_pages,
        'total': total,
    }

    return render(request, 'incomes/money_transfer_in.html', context=context)


def org_debt_payment_in(request, id):
    account = get_object_or_404(Bank, id=id)
    current_org = get_object_or_404(CustomUser, username=request.user.username).organization
    org_debt_payment_in = OrgDebtPayment.objects.filter(to_bank=account).order_by("-id")

    context = {}

    if 'from' in request.GET:
        time = request.GET['from'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            org_debt_payment_in = org_debt_payment_in.filter(date__gte=t)
            context['from'] = request.GET['from']

        # time = datetime()

    if 'to' in request.GET:
        time = request.GET['to'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            org_debt_payment_in = org_debt_payment_in.filter(date__lte=t)
            context['to'] = request.GET['to']

    p = Paginator(org_debt_payment_in, 30)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)

    index = page_obj.number - 1
    max_index = len(p.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = list(p.page_range)[start_index:end_index]
    total_pages = p.num_pages

    total = 0
    for p in org_debt_payment_in:
        total += p.amount

    context = {
        'payments': org_debt_payment_in,
        'account': account,
        'page_obj': page_obj,
        'page_range': page_range,
        'total_pages': total_pages,
        'total': total,
    }

    return render(request, 'incomes/org_debt_payment_in.html', context=context)


def product_transfer_payment_in(request, id):
    account = get_object_or_404(Bank, id=id)
    current_org = get_object_or_404(CustomUser, username=request.user.username).organization
    product_transfer_payment_in = TransferPayment.objects.filter(to_bank=account).order_by("-id")

    context = {}

    if 'from' in request.GET:
        time = request.GET['from'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            product_transfer_payment_in = product_transfer_payment_in.filter(datetime__gte=t)
            context['from'] = request.GET['from']

        # time = datetime()

    if 'to' in request.GET:
        time = request.GET['to'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            product_transfer_payment_in = product_transfer_payment_in.filter(datetime__lte=t)
            context['to'] = request.GET['to']

    p = Paginator(product_transfer_payment_in, 30)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)

    index = page_obj.number - 1
    max_index = len(p.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = list(p.page_range)[start_index:end_index]
    total_pages = p.num_pages

    total = 0
    for p in product_transfer_payment_in:
        total += p.amount

    context = {
        'payments': product_transfer_payment_in,
        'account': account,
        'page_obj': page_obj,
        'page_range': page_range,
        'total_pages': total_pages,
        'total': total,
    }

    return render(request, 'incomes/product_transfer_payment_in.html', context=context)


def additional_income(request, id):
    account = get_object_or_404(Bank, id=id)
    current_org = get_object_or_404(CustomUser, username=request.user.username).organization
    additional_income = AdditionalIncomes.objects.filter(bank=account).order_by("-id")

    context = {}

    if 'from' in request.GET:
        time = request.GET['from'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            additional_income = additional_income.filter(datetime__gte=t)
            context['from'] = request.GET['from']

        # time = datetime()

    if 'to' in request.GET:
        time = request.GET['to'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            additional_income = additional_income.filter(datetime__lte=t)
            context['to'] = request.GET['to']

    p = Paginator(additional_income, 30)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)

    index = page_obj.number - 1
    max_index = len(p.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = list(p.page_range)[start_index:end_index]
    total_pages = p.num_pages

    total = 0
    for p in additional_income:
        total += p.amount

    context = {
        'payments': additional_income,
        'account': account,
        'page_obj': page_obj,
        'page_range': page_range,
        'total_pages': total_pages,
        'total': total,
    }

    return render(request, 'incomes/additional_income.html', context=context)
