import json
from utils.pdf import render_to_pdf
from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views import View
from vendor.models import Vendor
from customuser.models import CustomUser
from product.models import Product, BaseProduct
from django.core import serializers
from bank.models import Bank
from tax.models import Tax
from django.contrib import messages
from datetime import datetime
from product.templatetags.product import cpu
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from customer.models import Customer
from .forms import *


def download_pdf(request, id):
    stk = get_object_or_404(Return, id=id)
    pwus = ReturnWithUnit.objects.filter(returned=stk)

    total = 0
    for p in pwus:
        total += p.price

    data = {
        "company": "Dennnis Ivanov Company",
        "address": "123 Street name",
        "city": "Vancouver",
        "state": "WA",
        "zipcode": "98663",
        "phone": "555-555-2345",
        "email": "youremail@dennisivy.com",
        "website": "dennisivy.com",
        'stk': stk,
        'pwus': pwus,
        'total': total,
    }
    pdf = render_to_pdf('pdf/return_pdf.html', data)

    filename = f"#RTN_00{stk.id}"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="{}"'.format(filename)
    return response


class SingleReturn(LoginRequiredMixin, View):
    def get(self,request, id, *args, **kwargs):
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        stk = get_object_or_404(Return, id=id)
        pwus = ReturnWithUnit.objects.filter(returned=stk)
        payments = ReturnPayment.objects.filter(returned=stk)
        banks = Bank.objects.filter(organization=current_user.organization)

        total = 0
        payed = 0
        for p in pwus: total += p.price
        for i in payments: payed += i.amount

        context = {
            'invoice': stk,
            'org': stk.user.organization,
            'pwus': pwus,
            'total': total,
            'payments': payments,
            'payed': payed,
            'banks':banks,
            'payable':total-payed
        }
        return render(request, 'return/single_return.html', context=context)

    def post(self, request, id, *args, **kwargs):
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        obj = get_object_or_404(Return,id=id)
        pwus = ReturnWithUnit.objects.filter(returned=obj)
        payments = ReturnPayment.objects.filter(returned=obj)
        payment_form = ReturnPaymentForm(request.POST or None)

        total = 0
        payed = 0
        for p in pwus: total += p.price
        for i in payments: payed += i.amount

        amount = float(request.POST['amount'])
        payable= float(total - payed)
        if payment_form.is_valid():
            if amount > payable:
                messages.error(request, f'Amount cannot be more than{total-payed}')
                return redirect(reverse("single_return", args=[id]))
            form = payment_form.save(commit=False)
            form.user = current_user
            form.returned = obj
            form.save()
            messages.success(request, 'Payment Has Been Made successfully')
        else:
            messages.error(request, str(payment_form.errors))
        return redirect(reverse("single_return",args=[id]))



class AddReturn(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get_products(self, org):
        result = []
        products = Product.objects.filter(organization=org)
        for p in products:
            result.append({
                'id': p.id,
                'name': p.product.name,
                'sku': p.product.sku,
                'price': p.sell_price,
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
        }
        return render(request, 'return/add_return.html', context=context)

    def post(self, request, *args, **kwargs):
        return_form = ReturnForm(request.POST or None)
        current_user = get_object_or_404(CustomUser, username=request.user.username)

        if return_form.is_valid():
            obj = return_form.save(commit=False)
            obj.user = current_user
            if 'customer' in request.POST:
                if str(request.POST['customer']) != '-1':
                    obj.customer = get_object_or_404(Customer, id=int(request.POST['customer']))
            messages.success(request, 'Products has been Returned  successfully')

            if 'pwu_input' in request.POST:
                pwus = json.loads(request.POST['pwu_input'])
                if len(pwus) > 0:
                    obj.save()
                    for pwu in pwus:
                        rp = ReturnWithUnit(
                            product=get_object_or_404(Product, id=int(pwu['id'])),
                            unit=float(pwu['unit']),
                            user=current_user,
                            returned=obj,
                            price=pwu['total_price']
                        )
                        rp.save()

            if 'payments_input' in request.POST:
                payments = json.loads(request.POST['payments_input'])
                for payment in payments:
                    p = ReturnPayment(returned=obj,
                                      bank=get_object_or_404(Bank, name=payment['name'],
                                                             organization=current_user.organization),
                                      amount=payment['amount'],
                                      note=payment['note'],
                                      user=current_user)
                    p.save()
            else:
                get_object_or_404(CustomUser, id=-1)
        else:
            messages.error(request, str(return_form.errors))
        return redirect(reverse('return'))


class ReturnView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        purchases = Return.objects.filter(user__organization=current_org).order_by('-id')
        returns = ReturnWithUnit.objects.filter(user__organization=current_org)
        payment = ReturnPayment.objects.filter(user__organization=current_org)
        context = {}
        if 'customer' in request.GET:
            customer_id = int(request.GET['customer'])
            if customer_id >= 0:
                purchases = purchases.filter(customer_id=customer_id)
                returns = returns.filter(returned__customer_id=customer_id)
                payment = payment.filter(returned__customer_id=customer_id)
                context['customer_id'] = customer_id

        if 'from' in request.GET:
            time = request.GET['from'].split('/')
            if len(time) == 3:
                t = datetime(int(time[2]), int(time[1]), int(time[0]))
                purchases = purchases.filter(datetime__gte=t)
                returns = returns.filter(returned__datetime__gte=t)
                payment = payment.filter(returned__datetime__gte=t)

                context['from'] = request.GET['from']

            # time = datetime()
        if 'to' in request.GET:
            time = request.GET['to'].split('/')
            if len(time) == 3:
                t = datetime(int(time[2]), int(time[1]), int(time[0]))
                purchases = purchases.filter(datetime__lte=t)
                returns = returns.filter(returned__datetime__lte=t)
                payment = payment.filter(returned__datetime__lte=t)
                context['to'] = request.GET['to']
        r_total = 0
        p_total = 0
        for r in returns:
            r_total += r.price
        for p in payment:
            p_total += p.amount

        context['purchases'] = purchases
        context['total'] = r_total
        context['r_payment'] = p_total
        context['customers'] = Customer.objects.filter(belongs_to=current_org)

        return render(request, 'return/returns.html', context=context)
