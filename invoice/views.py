import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views import View
from .models import Invoice
from customuser.models import CustomUser
from product.models import Product, BaseProduct
from django.core import serializers
from bank.models import Bank
from tax.models import Tax
from django.contrib import messages
from datetime import datetime
from customer.models import Customer
from .forms import InvoiceForm
from product.templatetags import product
from .models import SoldProduct, Payment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.http import JsonResponse
from utils.pdf import render_to_pdf
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.core.mail import send_mail, EmailMessage
from AMS.settings import EMAIL_HOST_USER, EMAILS_TO_SEND, COMPANY_NAME
from django.template.loader import render_to_string
from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from django.http import HttpResponse
import datetime
import xlwt


def send_email(request, id):
    try:
        invoice = get_object_or_404(Invoice, id=id)
        html_message = loader.render_to_string(
            'email.html', {
                'id': id
            }
        )
        send_mail(
            "Middle Asia - Invoice",
            f'',
            EMAIL_HOST_USER,
            [invoice.customer.email, ],
            fail_silently=False,
            html_message=html_message
        )
        messages.success(request, 'email has been sent successfully')
    except:
        messages.error(request, 'this customer does not have email')
    return redirect(reverse('single_invoice', kwargs={'id': id}))


def download_pdf(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    pwus = SoldProduct.objects.filter(invoice=invoice)
    payments = Payment.objects.filter(invoice=invoice)
    total = 0
    payed = 0
    for i in pwus: total += i.price
    for i in payments: payed += i.amount
    data = {
        "company": "Dennnis Ivanov Company",
        "address": "123 Street name",
        "city": "Vancouver",
        "state": "WA",
        "zipcode": "98663",
        "phone": "555-555-2345",
        "email": "youremail@dennisivy.com",
        "website": "dennisivy.com",
        'invoice': invoice,
        'pwus': pwus,
        'payments': payments,
        'total': total,
        'payed': payed,
        'invoice': invoice,
        'debt': total - payed

    }
    pdf = render_to_pdf('pdf/invoice.html', data)
    filename = f"#INV_00{invoice.id}"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="{}"'.format(filename)
    return response






def export_excel(request):
    response = HttpResponse(content_type='application/ms_excel')
    response['Conten-Disposition'] = 'attachment; filename = Invoice' + str(datetime.datetime.now()) + '.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Invoice', 'Customer')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['id', 'customer__name', 'user__organization__name', 'soldproduct__price', 'payment__amount', 'datetime']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    rows = Invoice.objects.filter(user=request.user).values_list(
         'id', 'customer__name', 'user__organization__name', 'soldproduct__price',  'payment__amount', 'datetime')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    return response


@login_required(login_url='/login/')
def single_invoice(request, id, *args, **kwargs):
    invoice = get_object_or_404(Invoice, id=id)
    pwus = SoldProduct.objects.filter(invoice=invoice)
    payments = Payment.objects.filter(invoice=invoice)
    total = 0
    payed = 0
    for i in pwus: total += i.price
    for i in payments: payed += i.amount
    context = {
        'invoice': invoice,
        'org': invoice.user.organization,
        'pwus': pwus,
        'total': total,
        'tax': total * (invoice.tax.percent / 100),
        'payments': payments,
        'payed': payed
    }
    return render(request, 'invoice/single_invoice.html', context=context)


@csrf_exempt
def get_product_stock(request, id):
    current_org = get_object_or_404(CustomUser, username=request.user.username).organization
    stock = product.cpu(Product.objects.get(id=id).product, current_org)
    return JsonResponse({'stock': stock})


class AddInvoice(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get_products(self, org):
        result = []
        products = Product.objects.filter(organization=org)
        for p in products:
            result.append({
                'id': p.id,
                'sku': p.product.sku,
                'name': p.product.name,
                'price': p.sell_price,
                # 'stock': product.cpu(p.product, org)
            })
        return result

    def get(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        context = {
            'products': json.dumps(self.get_products(current_org)),
            'products_list': self.get_products(current_org),
            'banks': Bank.objects.filter(organization=current_org),
            'methods': [{'id': i.id, 'name': i.name} for i in Bank.objects.filter(organization=current_org)],
            'customers': Customer.objects.filter(belongs_to=current_org),
            'taxes': Tax.objects.all()
        }
        return render(request, 'invoice/add_invoice.html', context=context)

    def post(self, request, *args, **kwargs):
        purchase_form = InvoiceForm(request.POST or None)
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        # print(request.POST)
        if purchase_form.is_valid():
            obj = purchase_form.save(commit=False)
            obj.tax = get_object_or_404(Tax, percent=request.POST['tax'])
            obj.user = current_user
            if 'customer' in request.POST:
                if str(request.POST['customer']) != '-1':
                    obj.customer = get_object_or_404(Customer, id=int(request.POST['customer']))

            messages.success(request, 'Purchase has been made successfully')

            if 'pwu_input' in request.POST:
                pwus = json.loads(request.POST['pwu_input'])
                if len(pwus) > 0:
                    obj.save()
                    for pwu in pwus:
                        bp = SoldProduct(
                            product_id=pwu['id'],
                            unit=pwu['unit'],
                            price=pwu['total_price'],
                            user=current_user,
                            invoice=obj
                        )
                        bp.save()
            if 'payments_input' in request.POST:
                payments = json.loads(request.POST['payments_input'])
                for payment in payments:
                    p = Payment(invoice=obj,
                                bank=get_object_or_404(Bank, name=payment['name'],
                                                       organization=current_user.organization),
                                amount=payment['amount'],
                                note=payment['note'],
                                user=current_user)
                    p.save()
            else:
                get_object_or_404(CustomUser, id=-1)
        else:
            messages.error(request, str(purchase_form.errors))
        return redirect(reverse('invoices'))


class InvoiceView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        invoices = Invoice.objects.filter(user__organization=current_org).order_by('-id')
        sold_product = SoldProduct.objects.filter(user__organization=current_org)
        payment = Payment.objects.filter(user__organization=current_org)

        context = {}
        if 'customer' in request.GET:
            customer_id = int(request.GET['customer'])
            if customer_id >= 0:
                invoices = invoices.filter(customer_id=customer_id)
                sold_product = sold_product.filter(invoice__customer_id=customer_id)
                payment = payment.filter(invoice__customer_id=customer_id)
                context['customer_id'] = customer_id
        if 'from' in request.GET:
            time = request.GET['from'].split('/')
            if len(time) == 3:
                t = datetime(int(time[2]), int(time[1]), int(time[0]))
                invoices = invoices.filter(datetime__gte=t)
                sold_product = sold_product.filter(invoice__datetime__gte=t)
                payment = payment.filter(invoice__datetime__gte=t)
                context['from'] = request.GET['from']

            # time = datetime()

        if 'to' in request.GET:
            time = request.GET['to'].split('/')
            if len(time) == 3:
                t = datetime(int(time[2]), int(time[1]), int(time[0]))
                invoices = invoices.filter(datetime__lte=t)
                sold_product = sold_product.filter(invoice__datetime__lte=t)
                payment = payment.filter(invoice__datetime__lte=t)
                context['to'] = request.GET['to']

        p = Paginator(invoices, 30)
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

        context['invoices'] = invoices
        context['customers'] = Customer.objects.filter(belongs_to=current_org)
        context['page_obj'] = page_obj
        context['page_range'] = page_range
        context['total_pages'] = total_pages

        return render(request, 'invoice/invoices.html', context=context)


def edit_invoice(request, id, *args, **kwargs):
    invoice = Invoice.objects.filter(id=id)
    sold_products = SoldProduct.objects.filter(invoice=invoice)

    context = {
        'sold_products': sold_products
    }
    return render(request, 'invoice/edit_invoice.html', context=context)
