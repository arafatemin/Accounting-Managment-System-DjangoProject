from django.contrib import messages
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views import View
from django.db.models import Avg, Sum, F, Func
from customer.models import Customer
from customuser.models import CustomUser
from fromstock.models import ProductWithUnit as ProductsFromStock
from invoice.models import Payment as InvoicePayment, Invoice, SoldProduct
from additional.models import AdditionalIncomes, AdditionalOutcomes, OutcomeCategory
from purchase.models import Payment as PurchasePayment, BoughtProduct
from purchase.models import *
from itertools import chain
from purchase.models import BoughtProduct as PurchaseBoughtProducts
from organization.models import Organization
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from product_transfer.models import *
from product.templatetags.product import cpu
from django.template import Library
from product.models import Product
from product.templatetags.product import cpu
from invoice.models import Payment as InvoicePayment
from additional.models import AdditionalIncomes, AdditionalOutcomes
from bank.models import Bank, Transfer
from purchase.models import Payment as PurchasePayment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import datetime

from returnproduct.models import ReturnWithUnit
from vendor.models import Vendor


def get_date(i):
    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        return now - i.date
    except:
        return now - i.datetime


@login_required(login_url='/login/')
def by_organization(request, *args, **kwargs):
    if request.user.is_superuser:
        date = ''
        context = {
            'organizations': Organization.objects.all()
        }
        if 'from' in request.GET:
            context['from'] = request.GET['from']
            date += f'---{context["from"]}'

        if 'to' in request.GET:
            context['to'] = request.GET['to']
            date += f'---{context["to"]}'
        context['date'] = date

        return render(request, 'report/by_organization.html', context=context)
    return redirect(reverse('index'))


@login_required(login_url='/login/')
def balance_sheet(request, *args, **kwargs):
    context = {}
    current_org = get_object_or_404(CustomUser, username=request.user.username).organization
    invoice_payment = InvoicePayment.objects.filter(user__organization=current_org)
    sold_product = SoldProduct.objects.filter(user__organization=current_org)
    outcomes = AdditionalOutcomes.objects.filter(user__organization=current_org)

    if 'from' in request.GET:
        time = request.GET['from'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            outcomes = outcomes.filter(datetime__gte=t)
            invoice_payment = invoice_payment.filter(invoice__datetime__gte=t)
            sold_product = sold_product.filter(invoice__datetime__gte=t)
            context['from'] = request.GET['from']

    if 'to' in request.GET:
        time = request.GET['to'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            outcomes = outcomes.filter(datetime__lte=t)
            invoice_payment = invoice_payment.filter(invoice__datetime__lte=t)
            sold_product = sold_product.filter(invoice__datetime__lte=t)
            context['to'] = request.GET['to']

    context['outcome_category'] = OutcomeCategory.objects.filter(user__organization=current_org)

    context['pay_total'] = invoice_payment.aggregate(Sum('amount'))
    context['buy_total'] = sold_product.annotate(
        total_price=F('unit') * F('product__price')).aggregate(Sum('total_price'))

    context['sell_total'] = sold_product.aggregate(Sum('price'))
    context['out_total'] = outcomes.aggregate(Sum('amount'))
    context['unpaid'] = outcomes.aggregate(Sum('amount'))

    return render(request, 'report/balance_sheet.html', context=context)


@login_required(login_url='/login/')
def product_report(request, *args, **kwargs):
    context = {}
    current_org = get_object_or_404(CustomUser, username=request.user.username).organization
    outcomes = AdditionalOutcomes.objects.filter(user__organization=current_org)
    invoice_payment = InvoicePayment.objects.filter(user__organization=current_org)

    product_from_stock = ProductsFromStock.objects.filter(user__organization=current_org)
    transferred_to_products = TransferedProduct.objects.filter(transfer__to_org=current_org)
    purchased_products = BoughtProduct.objects.filter(user__organization=current_org)
    sold_product = SoldProduct.objects.filter(user__organization=current_org)
    returned_products = ReturnWithUnit.objects.filter(user__organization=current_org)
    transferred_from_products = TransferedProduct.objects.filter(transfer__from_org=current_org)

    if 'from' in request.GET:
        time = request.GET['from'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            invoice_payment = invoice_payment.filter(date__gte=t)
            outcomes = outcomes.filter(datetime__gte=t)
            context['from'] = request.GET['from']

    if 'to' in request.GET:
        time = request.GET['to'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            invoice_payment = invoice_payment.filter(date__lte=t)
            outcomes = outcomes.filter(datetime__lte=t)
            context['to'] = request.GET['to']

    context['outcome_category'] = OutcomeCategory.objects.all()

    context['product_from_stock'] = product_from_stock.annotate(
        total_price=F('unit') * F('price')).aggregate(Sum('total_price'))
    context['transferred_to_products'] = transferred_to_products.aggregate(Sum('price'))
    context['transferred_from_products'] = transferred_from_products.annotate(
        total_price=F('unit') * F('product__price')).aggregate(Sum('total_price'))
    context['purchased_products'] = purchased_products.aggregate(Sum('price'))
    context['sell_total'] = sold_product.aggregate(Sum('price'))

    context['buy_total'] = sold_product.annotate(
        total_price=F('unit') * F('product__price')).aggregate(Sum('total_price'))
    context['pay_total'] = invoice_payment.aggregate(Sum('amount'))
    context['return_total'] = returned_products.aggregate(Sum('price'))
    context['return_buy_total'] = returned_products.annotate(
        total_price=F('unit') * F('product__price')).aggregate(Sum('total_price'))
    context['out_total'] = outcomes.aggregate(Sum('amount'))

    return render(request, 'report/product_report.html', context=context)


class IncomeReport(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        invoice_payment = InvoicePayment.objects.filter(user__organization=current_org)
        incomes = AdditionalIncomes.objects.filter(user__organization=current_org)
        transfer_payments = TransferPayment.objects.filter(user__organization=current_org)
        transfers = Transfer.objects.filter(to_account__organization=current_org)
        context = {}

        if 'from' in request.GET:
            time = request.GET['from'].split('/')
            if len(time) == 3:
                t = datetime(int(time[2]), int(time[1]), int(time[0]))
                invoice_payment = invoice_payment.filter(date__gte=t)
                incomes = incomes.filter(datetime__gte=t)
                transfer_payments = transfer_payments.filter(datetime__gte=t)
                transfers = transfers.filter(datetime__gte=t)
                context['from'] = request.GET['from']

            # time = datetime()

        if 'to' in request.GET:
            time = request.GET['to'].split('/')
            if len(time) == 3:
                t = datetime(int(time[2]), int(time[1]), int(time[0]))
                invoice_payment = invoice_payment.filter(date__lte=t)
                incomes = incomes.filter(datetime__lte=t)
                transfer_payments = transfer_payments.filter(datetime__gte=t)
                transfers = transfers.filter(datetime__gte=t)
                context['to'] = request.GET['to']

        total = 0
        result_list = sorted(chain(invoice_payment, incomes, transfer_payments, transfers), key=get_date)

        page_number = request.GET.get('page', 1)

        paginator = Paginator(result_list, 50)

        try:
            page_obj = paginator.get_page(page_number)  # returns the desired page object
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        index = page_obj.number - 1
        max_index = len(paginator.page_range)
        start_index = index - 5 if index >= 5 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        page_range = list(paginator.page_range)[start_index:end_index]
        total_pages = paginator.num_pages

        for r in result_list:
            total += r.amount
        context['page_obj'] = page_obj
        context['page_range'] = page_range
        context['total_pages'] = total_pages

        context['total'] = total
        return render(request, 'report/by_income.html', context=context)


@login_required(login_url='/login/')
def outcome_report(request, *args, **kwargs):
    context = {}
    current_org = get_object_or_404(CustomUser, username=request.user.username).organization
    outcomes = AdditionalOutcomes.objects.filter(user__organization=current_org)
    purchases = PurchasePayment.objects.filter(user__organization=current_org)
    transfers = Transfer.objects.filter(from_account__organization=current_org)

    if 'from' in request.GET:
        time = request.GET['from'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            outcomes = outcomes.filter(datetime__gte=t)
            purchases = purchases.filter(date__gte=t)
            transfers = purchases.filter(date__gte=t)
            context['from'] = request.GET['from']

    if 'to' in request.GET:
        time = request.GET['to'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            outcomes = outcomes.filter(datetime__lte=t)
            purchases = purchases.filter(date__lte=t)
            transfers = purchases.filter(date__lte=t)
            context['to'] = request.GET['to']

    if 'category' in request.GET:
        category_id = int(request.GET['category'])
        if category_id != -1:
            purchases = []
            outcomes.filter(category_id=category_id)
        context['category_id'] = category_id
    total = 0
    result_list = sorted(chain(outcomes, purchases, transfers), key=get_date)

    page_number = request.GET.get('page', 1)

    paginator = Paginator(result_list, 50)

    try:
        page_obj = paginator.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    index = page_obj.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = list(paginator.page_range)[start_index:end_index]
    total_pages = paginator.num_pages

    for r in result_list:
        total += r.amount
    context['page_obj'] = page_obj
    context['page_range'] = page_range
    context['total_pages'] = total_pages
    context['categories'] = OutcomeCategory.objects.filter(user__organization=current_org)
    context['total'] = total
    return render(request, 'report/by_outcome.html', context=context)


def single_org_report(request, id):
    result = ""
    organization = get_object_or_404(Organization, id=id)
    products = Product.objects.filter(organization=organization)

    page_number = request.GET.get('page', 1)

    paginator = Paginator(products, 50)

    try:
        page_obj = paginator.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    index = page_obj.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = list(paginator.page_range)[start_index:end_index]
    total_pages = paginator.num_pages

    for p in page_obj.object_list:
        url = reverse('product_detail', kwargs={'id': p.product.id})
        unit = cpu(p.product, organization)
        total = p.price * unit
        total = round(total, 2)
        result += f"<tr>" \
                  f"<td><a href='{url}'>{p.product.sku} --- {p.product.name}</a></td>" \
                  f"<td>{unit} {p.product.type}</td>" \
                  f"<td>{p.price} SAR</td>" \
                  f"<td>{p.sell_price} SAR</td>" \
                  f"<td>{total} SAR</td>" \
                  f"</tr>"

    context = {
        'organization': organization,
        'page_obj': page_obj,
        'result': result,
        'page_range': page_range,
        'total_pages': total_pages,

    }
    return render(request, 'report/single_org_report.html', context=context)


@login_required(login_url='/login/')
def general_report(request, *args, **kwargs):
    global filter_query
    current_org = get_object_or_404(CustomUser, username=request.user.username).organization

    vendor_list = [
        {
            'id': obj.id,
            'name': obj.name,
        }
        for obj in Vendor.objects.filter(belongs_to=current_org)
    ]

    customer_list = [
        {
            'id': obj.id,
            'name': obj.name,
        }
        for obj in Customer.objects.filter(belongs_to=current_org)
    ]

    outcome_list = [
        {
            'id': obj.id,
            'name': obj.name,
        }
        for obj in OutcomeCategory.objects.filter(user__organization=current_org)
    ]

    organization_list = [
        {
            'id': obj.id,
            'name': obj.name,
        }
        for obj in Organization.objects.all()
    ]

    context = {
        'customers': Customer.objects.filter(belongs_to=current_org),
        'accounts': Bank.objects.filter(organization=current_org),
        'vendors': Vendor.objects.filter(belongs_to=current_org),
        'outcome_category': OutcomeCategory.objects.filter(user__organization=current_org),
        'organizations': Organization.objects.all(),

        'vendor_list': vendor_list,
        'customer_list': customer_list,
        'outcome_list': outcome_list,
        'organization_list': organization_list,

    }

    if 'type' in request.GET:
        filter_type = request.GET['type']
        filter_query = ''
        result_list = []
        total = ''
        filter_query = request.GET.getlist('filter_query')
        account = request.GET['account']
        count = 0

        if filter_type == '-1':
            messages.error(request, 'Please Select A Type')
        else:
            # customer filter
            if filter_type == 'customer':
                if filter_query:
                    invoices = Invoice.objects.filter(customer__name__in=filter_query,
                                                      user__organization=current_org)
                    invoice_payments = InvoicePayment.objects.filter(invoice__customer__name__in=filter_query)

                    result_list = sorted(chain(invoices, invoice_payments), key=get_date)
                    count = invoices.count() + invoice_payments.count()

            # vendor filter
            if filter_type == 'vendor':
                messages.error(request, filter_query)

            # outcome filter

            if filter_type == 'outcome':
                if filter_query:
                    result_list = AdditionalOutcomes.objects.filter(category__name__in=filter_query,
                                                                    user__organization=current_org)
                    if account != '-1':
                        result_list = AdditionalOutcomes.objects.filter(category__name__in=filter_query,
                                                                        user__organization=current_org,
                                                                        bank__id=account)
                else:
                    filter_query = OutcomeCategory.objects.values('name').filter(user__organization=current_org)
                    result_list = AdditionalOutcomes.objects.filter(user__organization=current_org)
                    if account != '-1':
                        result_list = AdditionalOutcomes.objects.filter(user__organization=current_org,
                                                                        bank__id=account)
                if 'from' in request.GET:
                    time = request.GET['from'].split('/')
                    if len(time) == 3:
                        t = datetime(int(time[2]), int(time[1]), int(time[0]))
                        result_list = AdditionalOutcomes.objects.filter(category__name__in=filter_query,
                                                                        user__organization=current_org,
                                                                        datetime__gte=t)
                if 'to' in request.GET:
                    time = request.GET['to'].split('/')
                    if len(time) == 3:
                        t = datetime(int(time[2]), int(time[1]), int(time[0]))
                        result_list = AdditionalOutcomes.objects.filter(category__name__in=filter_query,
                                                                        user__organization=current_org,
                                                                        datetime__lte=t)

                total = result_list.aggregate(Sum('amount'))
                total = total['amount__sum']

            if filter_type == 'organization':
                messages.error(request, filter_query)

        context['result_list'] = result_list
        context['filter_type'] = filter_type
        context['total'] = total
        context['filter_query'] = filter_query
        context['from'] = request.GET['from']
        context['to'] = request.GET['to']
        context['count'] = count

    return render(request, 'report/general_report.html', context=context)
