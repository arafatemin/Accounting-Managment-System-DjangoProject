import json

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views import View
from .models import Purchase
from vendor.models import Vendor
from customuser.models import CustomUser
from product.models import Product, BaseProduct
from django.core import serializers
from bank.models import Bank
from tax.models import Tax
from .forms import ModelForm, Payment, PaymentForm, BoughtProductForm, BoughtProduct, ReturnedProduct, PurchaseForm, \
    Purchase
from django.contrib import messages
from datetime import  datetime
from product.templatetags.product import cpu
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from utils.pdf import render_to_pdf
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.core.mail import send_mail,EmailMessage
from AMS.settings import EMAIL_HOST_USER,EMAILS_TO_SEND,COMPANY_NAME
from django.template.loader import render_to_string
from django.template import loader


def send_email(request,id):
    try:
        purchase = get_object_or_404(Purchase, id=id)
        html_message = loader.render_to_string(
            'email_purchase.html',{
                'id':id
            }
        )
        send_mail(
            "Middle Asia - Invoice",
            f'',
            EMAIL_HOST_USER,
            [purchase.customer.email,],
            fail_silently=False,
            html_message=html_message
        )
        messages.success(request,'email has been sent successfully')
    except:
        messages.error(request,'this vendor does not have email')
    return redirect(reverse('single_purchase',kwargs={'id':id}))


def download_pdf(request, id):
    purchase = get_object_or_404(Purchase, id=id)
    pwus = BoughtProduct.objects.filter(purchase=purchase)
    payments = Payment.objects.filter(purchase=purchase)
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
        'invoice': purchase,
        'pwus': pwus,
        'payments': payments,
        'total':total,
        'payed':payed,
        'debt':total - payed

    }
    pdf = render_to_pdf('pdf/invoice.html', data)
    return HttpResponse(pdf, content_type='application/pdf')


@login_required(login_url='/login/')
def single_purchase(request,id,*args,**kwargs):
    purchase = get_object_or_404(Purchase,id=id)
    pwus = BoughtProduct.objects.filter(purchase=purchase)
    payments = Payment.objects.filter(purchase=purchase)
    total = 0
    payed = 0
    for i in pwus: total += i.price
    for i in payments: payed += i.amount
    context = {
        'invoice': purchase,
        'org': get_object_or_404(CustomUser,username=request.user.username).organization,
        'pwus': pwus,
        'total':total,
        'tax':total*(purchase.tax.percent / 100),
        'payments':payments,
        'payed':payed
    }
    return render(request,'purchase/single_purchase.html',context=context)



class AddPurchase(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = ''

    def get_products(self, org):
        result = []
        products = Product.objects.filter(organization=org)
        for p in products:
            result.append({
                'id': p.id,
                'name': p.product.name,
                'sku':p.product.sku,
                'price': p.price,
            })
        return result

    def get(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        context = {
            'products': json.dumps(self.get_products(current_org)),
            'products_list': self.get_products(current_org),
            'banks': Bank.objects.filter(organization=current_org),
            'methods': [{'id': i.id, 'name': i.name} for i in Bank.objects.filter(organization=current_org)],
            'vendors': Vendor.objects.filter(belongs_to=current_org),
            'taxes': Tax.objects.all()
        }
        return render(request, 'purchase/add_purchase.html', context=context)

    def post(self, request, *args, **kwargs):
        purchase_form = PurchaseForm(request.POST or None)
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        print(request.POST)
        if purchase_form.is_valid():
            obj = purchase_form.save(commit=False)
            obj.tax = get_object_or_404(Tax, percent=request.POST['tax'])
            obj.user = current_user

            messages.success(request, 'Purchase has been made successfully')
            if 'pwu_input' in request.POST:
                pwus = json.loads(request.POST['pwu_input'])
                if len(pwus) > 0:
                    obj.save()
                    for pwu in pwus:
                        bp = BoughtProduct(
                            product_id=pwu['id'],
                            unit=pwu['unit'],
                            price=pwu['total_price'],
                            user=current_user,
                            purchase=obj
                        )
                        bp.save()
            if 'payments_input' in request.POST:
                payments = json.loads(request.POST['payments_input'])
                for payment in payments:
                    p = Payment(purchase=obj,
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
        return redirect(reverse('add_purchase'))


class PurchaseView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = ''
    def get(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        purchases = Purchase.objects.filter(user__organization=current_org)
        products = BoughtProduct.objects.filter(user__organization=current_org)
        payments = Payment.objects.filter(user__organization=current_org)

        total = 0
        for p in products:
            total += p.price

        total_payment = 0
        for p in payments:
            total_payment += p.amount


        context = {}
        if 'vendor' in request.GET:
            vendor_id = int(request.GET['vendor'])
            if vendor_id >= 0:
                purchases = purchases.filter(customer_id=vendor_id)
                context['vendor_id'] = vendor_id
        if 'from' in request.GET:
            time = request.GET['from'].split('/')
            if len(time) == 3:
                t = datetime(int(time[2]),int(time[1]),int(time[0]))
                purchases = purchases.filter(datetime__gte=t)
                context['from'] = request.GET['from']

            # time = datetime()

        if 'to' in request.GET:
            time = request.GET['to'].split('/')
            if len(time) == 3:
                t = datetime(int(time[2]),int(time[1]),int(time[0]))
                purchases = purchases.filter(datetime__lte=t)
                context['to'] = request.GET['to']

        context['purchases'] = purchases
        context['total'] = total
        context['total_payment'] = total_payment
        context['vendors'] = Vendor.objects.filter(belongs_to=current_org)
        print(context)

        return render(request, 'purchase/purchase.html', context=context)
