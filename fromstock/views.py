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
from .models import ProductInStock,ProductWithUnit
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required







def download_pdf(request, id):
    stk = get_object_or_404(ProductInStock, id=id)
    pwus = ProductWithUnit.objects.filter(stock=stk)



    total = 0
    for p in pwus:
        total += p.price * p.unit

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
        'total':total,
    }
    pdf = render_to_pdf('pdf/stock_pdf.html', data)

    filename = f"#STK_00{stk.id}"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="{}"'.format(filename)
    return response



@login_required(login_url='/login/')
def single_stock(request,id,*args,**kwargs):
    stk = get_object_or_404(ProductInStock,id=id)
    pwus = ProductWithUnit.objects.filter(stock=stk)
    total = 0
    for p in pwus:
        total += p.price * p.unit
    context = {
        'stk':stk,
        'pwus': pwus,
        'total':total
    }
    return render(request,'fromstock/single_stock.html',context=context)




class AddSotck(LoginRequiredMixin,View):
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
                'price': p.price,
            })
        return result

    def get(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        context = {
            'products': json.dumps(self.get_products(current_org)),
            'products_list': self.get_products(current_org),
        }
        return render(request, 'fromstock/add_stock.html', context=context)

    def post(self, request, *args, **kwargs):
        current_user = get_object_or_404(CustomUser, username=request.user.username)

        obj = ProductInStock(
            note=request.POST['note'] if 'note' in request.POST else ''
        )
        obj.user = current_user
        obj.save()
        messages.success(request, 'Sotck has been made successfully')
        if 'bucket' in request.POST:
            pwus = json.loads(request.POST['bucket'])
            if len(pwus) > 0:
                obj.save()
                for pwu in pwus:
                    print(pwus)
                    bp = ProductWithUnit(
                        product=get_object_or_404(Product,id=int(pwu['id'])),
                        unit=float(pwu['unit']),
                        user=current_user,
                        stock=obj,
                        price=pwu['price']
                    )
                    bp.save()
        else:
            get_object_or_404(CustomUser, id=-1)

        return redirect(reverse('add_stock'))


class StockView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = ''
    def get(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        purchases = ProductInStock.objects.filter(user__organization=current_org)
        fromstocks = ProductWithUnit.objects.filter(user__organization=current_org)
        context = {}
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
        f_total = 0
        for f in fromstocks:
            f_total += f.price * f.unit

        context['purchases'] = purchases
        context['total'] = f_total




        return render(request, 'fromstock/stocks.html', context=context)

def edit_stock(request,id):
    context={}
    return render(request, 'fromstock/edit_stock.html', context=context)