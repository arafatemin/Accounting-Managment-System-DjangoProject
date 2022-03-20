import json
from utils.pdf import render_to_pdf
from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views import View
from vendor.models import Vendor
from customuser.models import CustomUser
from product.models import Product, BaseProduct
from bank.models import Bank
from tax.models import Tax
from django.contrib import messages
from datetime import datetime
from .models import TransferedProduct, ProductTransfer, TransferPayment
from organization.models import Organization
from product.templatetags import product
from .forms import TransferForm
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


@login_required(login_url='/login/')
def download_pdf(request, id):
    stk = get_object_or_404(ProductTransfer, id=id)
    pwus = TransferedProduct.objects.filter(transfer=stk)

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
        'stk': stk,
        'pwus': pwus,
        'total': total,
    }
    pdf = render_to_pdf('pdf/transfer_pdf.html', data)

    filename = f"#TRA_00{stk.id}"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="{}"'.format(filename)
    return response


@login_required(login_url='/login/')
def single_transfer(request, id):
    invoice = get_object_or_404(ProductTransfer, id=id)
    pwus = TransferedProduct.objects.filter(transfer=invoice)
    payments = TransferPayment.objects.filter(transfer=invoice)
    total = 0
    payed = 0
    for i in pwus: total += i.price
    for i in payments: payed += i.amount
    context = {
        'invoice': invoice,
        'org': get_object_or_404(CustomUser, username=request.user.username).organization,
        'pwus': pwus,
        'total': total,
        'tax': total * (invoice.tax.percent / 100),
        'payments': payments,
        'payed': payed
    }
    return render(request, 'product_transfer/single_transfer.html', context=context)


class AddTransfer(LoginRequiredMixin, View):
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
                # 'stock': product.cpu(p.product, org)
            })
        return result

    def get(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        context = {
            'products': json.dumps(self.get_products(current_org)),
            'products_list': self.get_products(current_org),
            'banks': Bank.objects.filter(organization=current_org),
            'other_banks': Bank.objects.filter(~Q(organization=current_org)),
            'methods': [{'id': i.id, 'name': i.name} for i in Bank.objects.filter(organization=current_org)],
            'methods_to': [{'id': i.id, 'name': i.name} for i in Bank.objects.filter(organization=current_org)],
            'methods_from': [{'id': c.id, 'name': c.name} for c in Bank.objects.filter(~Q(organization=current_org))],
            'organizations': Organization.objects.all().exclude(id=current_org.id),
            'taxes': Tax.objects.all()
        }
        return render(request, 'product_transfer/add_transfer.html', context=context)

    def post(self, request, *args, **kwargs):
        purchase_form = TransferForm(request.POST or None)
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        if purchase_form.is_valid():
            obj = purchase_form.save(commit=False)
            obj.tax = get_object_or_404(Tax, percent=request.POST['tax'])
            obj.from_org = current_user.organization
            obj.user = current_user
            messages.success(request, 'Transfer has been done successfully')
            if 'pwu_input' in request.POST:
                pwus = json.loads(request.POST['pwu_input'])
                if len(pwus) > 0:
                    obj.save()
                    for pwu in pwus:
                        bp = TransferedProduct(
                            product=get_object_or_404(Product, id=int(pwu['id'])),
                            unit=pwu['unit'],
                            price=pwu['total_price'] if obj.from_org != obj.to_org else 0,
                            user=current_user,
                            transfer=obj
                        )
                        bp.save()
            if ('payments_input' in request.POST):
                payments = json.loads(request.POST['payments_input'])
                for payment in payments:
                    p = TransferPayment(transfer=obj,
                                        to_bank=get_object_or_404(Bank, name=payment['to_name'],
                                                                  organization=current_user.organization),
                                        from_bank=get_object_or_404(Bank, name=payment['from_name'],
                                                                    organization=current_user.organization),
                                        amount=payment['amount'],
                                        note=payment['note'],
                                        user=current_user)
                    p.save()



            else:
                get_object_or_404(CustomUser, id=-1)
        else:
            messages.error(request, str(purchase_form.errors))
        return redirect(reverse('transfer'))


class TransferView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        transfers = ProductTransfer.objects.filter(Q(from_org=current_org) | Q(to_org=current_org)).order_by('-id')
        t_products = TransferedProduct.objects.filter(transfer__from_org=current_org)
        t_payment = TransferPayment.objects.filter(transfer__from_org=current_org)
        context = {}

        if 'from_org' in request.GET:
            from_org_id = int(request.GET['from_org'])
            if from_org_id >= 0:
                transfers = transfers.filter(to_org=current_org, from_org_id=from_org_id)
                t_products = t_products.filter(transfer__to_org=current_org, transfer__from_org_id=from_org_id)
                t_payment = t_payment.filter(transfer__to_org=current_org, transfer__from_org_id=from_org_id)
                context['from_org_id'] = from_org_id

        if 'to_org' in request.GET:
            to_org_id = int(request.GET['to_org'])
            if to_org_id >= 0:
                transfers = transfers.filter(to_org_id=to_org_id, from_org=current_org)
                t_products = t_products.filter(transfer__to_org_id=to_org_id, transfer__from_org=current_org)
                t_payment = t_payment.filter(transfer__to_org_id=to_org_id, transfer__from_org=current_org)
                context['to_org_id'] = to_org_id

        if 'from' in request.GET:
            time = request.GET['from'].split('/')
            if len(time) == 3:
                t = datetime(int(time[2]), int(time[1]), int(time[0]))
                transfers = transfers.filter(datetime__gte=t)
                t_products = t_products.filter(transfer__datetime__gte=t)
                t_payment = t_payment.filter(transfer__datetime__gte=t)
                context['from'] = request.GET['from']

            # time = datetime()

        if 'to' in request.GET:
            time = request.GET['to'].split('/')
            if len(time) == 3:
                t = datetime(int(time[2]), int(time[1]), int(time[0]))
                transfers = transfers.filter(datetime__lte=t)
                t_products = t_products.filter(transfer__datetime__gte=t)
                t_payment = t_payment.filter(transfer__datetime__gte=t)
                context['to'] = request.GET['to']

        tpr_total = 0
        tpy_total = 0

        for s in t_products:
            tpr_total += s.price

        for p in t_payment:
            tpy_total += p.amount

        context['tpr_total'] = tpr_total
        context['tpy_total'] = tpy_total

        context['transfers'] = transfers
        context['organization'] = Organization.objects.all()

        return render(request, 'product_transfer/product_transfer.html', context=context)
