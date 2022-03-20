from django.shortcuts import get_object_or_404, render, redirect, reverse
from additional.models import OutcomeCategory, AdditionalOutcomes
from bank.models import Bank, Transfer
from customuser.models import CustomUser
from customer.models import Customer
from invoice.models import Invoice, SoldProduct, Payment
from invoice.models import Payment as InvoicePayment
from product_transfer.models import ProductTransfer, TransferedProduct
from purchase.models import Purchase, BoughtProduct
from product.models import Product
from datetime import date
from django.db.models import Q
from datetime import datetime, timedelta, time
from returnproduct.models import ReturnWithUnit

# ***************** pdf ***********
from django.http import FileResponse, HttpResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from utils.pdf import render_to_pdf


def index_page(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    return render(request, 'AMS/index.html')


def account_a_day(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    current_date = date.today()

    today = datetime.now().date()
    tomorrow = today + timedelta(1)
    today_start = datetime.combine(today, time())
    today_end = datetime.combine(tomorrow, time())
    current_user = get_object_or_404(CustomUser, username=request.user.username)

    current_org = get_object_or_404(CustomUser, username=request.user.username).organization
    outcome_categories = OutcomeCategory.objects.filter(user__organization=current_org)
    invoices = Invoice.objects.filter(datetime__range=[today_start, today_end], user__organization=current_org).count()
    sold_product = SoldProduct.objects.filter(datetime__range=[today_start, today_end], user__organization=current_org)
    invoice_payment = InvoicePayment.objects.filter(date__range=[today_start, today_end],
                                                    user__organization=current_org)

    purchases = BoughtProduct.objects.filter(datetime__range=[today_start, today_end], user__organization=current_org)

    accounts = Bank.objects.filter(organization=current_org)



    product_transfer = TransferedProduct.objects.filter(datetime__range=[today_start, today_end],
                                                        user__organization=current_org)

    transfers = Transfer.objects.filter(date__range=[today_start, today_end],
                                                        user__organization=current_org)
    product_return = ReturnWithUnit.objects.filter(datetime__range=[today_start, today_end],
                                                   user__organization=current_org)
    outcomes = AdditionalOutcomes.objects.filter(datetime__range=[today_start, today_end],
                                                 user__organization=current_org)




    sold_total = 0
    for s in sold_product:
        sold_total += s.price + ((int(s.price) * int(s.invoice.tax.percent)) / 100)

    buy_total = 0
    for s in purchases:
        buy_total += s.price + ((int(s.price) * int(s.purchase.tax.percent)) / 100)


    invoice_payment_total = 0
    for i in invoice_payment:
        invoice_payment_total += i.amount



    buy_price = 0
    for s in sold_product:
        buy_price += s.product.price * s.unit

    product_transfer_price = 0
    for p in product_transfer:
        product_transfer_price += p.price

    product_return_price = 0
    for p in product_return:
        product_return_price += p.price

    outcome_total = 0
    for o in outcomes:
        outcome_total += o.amount

    context = {
        'invoices': invoices,
        'buy_total': buy_total,
        'purchases': purchases,
        'current_date': current_date,
        'outcome_categories': outcome_categories,
        'accounts': accounts,
        'sold_total': sold_total,
        'invoice_payment_total': invoice_payment_total,
        'buy_price': buy_price,
        'product_transfer_price': product_transfer_price,
        'product_return_price': product_return_price,
        'outcome_total': outcome_total,
        'transfers': transfers,

    }
    print(transfers.dates)
    return render(request, 'AMS/account_a_day.html', context=context)


#
# def pdf(request):
#     pass


def pdf(request):
    current_date = date.today()

    today = datetime.now().date()
    tomorrow = today + timedelta(1)
    today_start = datetime.combine(today, time())
    today_end = datetime.combine(tomorrow, time())

    current_org = get_object_or_404(CustomUser, username=request.user.username).organization
    outcome_categories = OutcomeCategory.objects.filter(user__organization=current_org)
    invoices = Invoice.objects.filter(datetime__range=[today_start, today_end], user__organization=current_org).count()
    sold_product = SoldProduct.objects.filter(datetime__range=[today_start, today_end], user__organization=current_org)
    invoice_payment = InvoicePayment.objects.filter(date__range=[today_start, today_end],
                                                    user__organization=current_org)

    purchases = Purchase.objects.filter(user__organization=current_org).count()
    buy_totals = BoughtProduct.objects.filter(datetime__range=[today_start, today_end], user__organization=current_org)
    accounts = Bank.objects.filter(organization=current_org)

    product_transfer = TransferedProduct.objects.filter(datetime__range=[today_start, today_end],
                                                        user__organization=current_org)
    product_return = ReturnWithUnit.objects.filter(datetime__range=[today_start, today_end],
                                                   user__organization=current_org)
    outcomes = AdditionalOutcomes.objects.filter(datetime__range=[today_start, today_end],
                                                 user__organization=current_org)
    sold_total = 0
    for s in sold_product:
        sold_total += s.price

    buy_total = 0
    for s in buy_totals:
        buy_total += s.price + ((int(s.price) * int(s.purchase.tax.percent)) / 100)


    invoice_payment_total = 0
    for i in invoice_payment:
        invoice_payment_total += i.amount

    buy_price = 0
    for s in sold_product:
        buy_price += s.product.price * s.unit

    product_transfer_price = 0
    for p in product_transfer:
        product_transfer_price += p.price

    product_return_price = 0
    for p in product_return:
        product_return_price += p.price

    outcome_total = 0
    for o in outcomes:
        outcome_total += o.amount

    data = {
        'invoices': invoices,
        'purchases': purchases,
        'current_date': current_date,
        'outcome_categories': outcome_categories,
        'accounts': accounts,
        'sold_total': sold_total,
        'invoice_payment_total': invoice_payment_total,
        'buy_price': buy_price,
        'buy_total': buy_total,
        'product_transfer_price': product_transfer_price,
        'product_return_price': product_return_price,
        'outcome_total': outcome_total,
    }

    pdf = render_to_pdf('AMS/pdf.html', data)

    response = HttpResponse(pdf, content_type='application/pdf')

    return response
