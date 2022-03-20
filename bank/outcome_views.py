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
from additional.models import AdditionalIncomes, AdditionalOutcomes, OutcomeCategory
from bank.models import *
from purchase.models import Payment as PurchasePayment
from purchase.models import DebtPayment
from purchase.models import DebtPayment
from product_transfer.models import *
from returnproduct.models import ReturnPayment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime


def additional_outcome(request, id):
    account = get_object_or_404(Bank, id=id)
    additional_outcome = AdditionalOutcomes.objects.filter(bank=account).order_by("-id")
    categories = OutcomeCategory.objects.all()

    context = {}

    if 'from' in request.GET:
        time = request.GET['from'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            additional_outcome = additional_outcome.filter(datetime__gte=t)
            categories = None
            context['from'] = request.GET['from']

    if 'to' in request.GET:
        time = request.GET['to'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            additional_outcome = additional_outcome.filter(datetime__lte=t)
            categories = None
            context['to'] = request.GET['to']

    p = Paginator(additional_outcome, 30)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = p.get_page(page_number)
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
    for p in additional_outcome:
        total += p.amount

    context = {
        'payments': additional_outcome,
        'account': account,
        'page_obj': page_obj,
        'page_range': page_range,
        'total_pages': total_pages,
        'total': total,
        'categories': categories,
    }

    return render(request, 'outcomes/additional_outcome.html', context=context)



# def single_outcome_cat(request, id):
#     account = get_object_or_404(Bank, id=id)
#     single_outcome_cat = AdditionalOutcomes.objects.filter(bank=account,category_id=id).order_by("-id")
#     categories = OutcomeCategory.objects.all()
#
#     context = {}
#
#     if 'from' in request.GET:
#         time = request.GET['from'].split('/')
#         if len(time) == 3:
#             t = datetime(int(time[2]), int(time[1]), int(time[0]))
#             additional_outcome = additional_outcome.filter(datetime__gte=t)
#             categories = None
#             context['from'] = request.GET['from']
#
#     if 'to' in request.GET:
#         time = request.GET['to'].split('/')
#         if len(time) == 3:
#             t = datetime(int(time[2]), int(time[1]), int(time[0]))
#             additional_outcome = additional_outcome.filter(datetime__lte=t)
#             categories = None
#             context['to'] = request.GET['to']
#
#     p = Paginator(additional_outcome, 30)
#     page_number = request.GET.get('page', 1)
#     try:
#         page_obj = p.get_page(page_number)
#     except PageNotAnInteger:
#         page_obj = p.page(1)
#     except EmptyPage:
#         page_obj = p.page(p.num_pages)
#
#     index = page_obj.number - 1
#     max_index = len(p.page_range)
#     start_index = index - 5 if index >= 5 else 0
#     end_index = index + 5 if index <= max_index - 5 else max_index
#     page_range = list(p.page_range)[start_index:end_index]
#     total_pages = p.num_pages
#
#     total = 0
#     for p in additional_outcome:
#         total += p.amount
#
#     context = {
#         'payments': additional_outcome,
#         'account': account,
#         'page_obj': page_obj,
#         'page_range': page_range,
#         'total_pages': total_pages,
#         'total': total,
#         'categories': categories,
#     }
#
#     return render(request, 'outcomes/additional_outcome.html', context=context)
