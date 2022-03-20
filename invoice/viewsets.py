import json

from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from customuser.models import CustomUser
from rest_framework import status
from product.models import Product,BaseProduct,ProductCategory,UnitType
from rest_framework import serializers
from django.contrib.auth import login,logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.sessions.backends.db import SessionStore
from rest_framework.authtoken import views
from product.templatetags.product import cpu
from tax.models import Tax
from customer.models import Customer
from bank.models import Bank
from .models import SoldProduct,Payment,ReturnedProduct,Invoice





class CustomRenderer(JSONRenderer):
    charset = 'utf-8'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('id','title')




class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ('percent','id')

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ('name','id')

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('name','id')

class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitType
        fields = ('name',)

class BaseProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    type = TypeSerializer(read_only=True)
    class Meta:
        model = BaseProduct
        fields = ('id','sku','image','name','category','type','barcode')


class InvoiceSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField('get_products')
    payments = serializers.SerializerMethodField('get_payments')
    tax      = TaxSerializer()
    customer = CustomerSerializer()
    class Meta:
        model = Invoice
        fields = ('id','tax','customer','products','payments','datetime')

    def get_products(self,invoice):
        return [
            {
                'product': p.product.product.name,
                'unit': f'{p.unit} {p.product.product.type}',
                'price':p.price,
            } for p in SoldProduct.objects.filter(invoice=invoice)
        ]

    def get_payments(self,invoice):
        return [
            {
                'bank': p.bank.name,
                'amount': p.amount
            }for p in Payment.objects.filter(invoice=invoice)
        ]

class ProductSerializer(serializers.ModelSerializer):
    product = BaseProductSerializer(read_only=True)
    count   = serializers.SerializerMethodField('get_product_count')
    class Meta:
        model = Product
        fields = ('id','product','price','sell_price','count')

    def get_product_count(self,product):
        request = self.context.get('request', None)
        return cpu(product=product.product,org=get_object_or_404(CustomUser,username=request.user.username).organization)




@csrf_exempt
def login_view(request):
    if request.method == "POST":
        users = CustomUser.objects.filter(username=request.POST['username'])
        if users.count() > 0:
            user  = users[0]
            if user.check_password(request.POST['password']):
                login(request,user)
                print(request.user)
                return JsonResponse({'success':True})
    return JsonResponse({'success': False})



class TaxViewSer(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaxSerializer
    queryset = Tax.objects.all()

class BankViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BankSerializer
    renderer_classes = [CustomRenderer]

    def get_queryset(self):
        current_org = get_object_or_404(CustomUser, username=self.request.user.username).organization
        return Bank.objects.filter(organization=current_org)

class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomerSerializer
    renderer_classes = [CustomRenderer]

    def get_queryset(self):
        current_org = get_object_or_404(CustomUser, username=self.request.user.username).organization
        return Customer.objects.filter(belongs_to=current_org)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    renderer_classes = [CustomRenderer]
    serializer_class = ProductSerializer
    def get_queryset(self):
        current_org = get_object_or_404(CustomUser, username=self.request.user.username).organization
        return Product.objects.filter(organization=current_org)

class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    renderer_classes = [CustomRenderer]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        current_org = get_object_or_404(CustomUser, username=self.request.user.username)
        return Invoice.objects.filter(user=current_org).order_by('-datetime')

@csrf_exempt
def add_invoice(request,*args,**kwargs):
    if request.method == "POST":
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        tax          = get_object_or_404(Tax,id=int(request.POST['tax']))
        customer     = request.POST['customer']
        products     = json.loads(request.POST['products'])
        payments = json.loads(request.POST['payments'])
        if str(customer) != '-1':
            customer = get_object_or_404(Customer,id=int(request.POST['customer']))
        else:
            customer = None

        i  = Invoice(
            customer=customer,
            user=current_user,
            tax=tax
        )
        i.save()


        for p in products:
            pwu = SoldProduct(
                invoice=i,
                user=current_user,
                price=p['price'] * p['unit'],
                product=get_object_or_404(Product,id=p['id']),
                unit=p['unit'],
            )
            pwu.save()

        for p in payments:
            payment = Payment(
                invoice=i,
                bank=get_object_or_404(Bank,id=p['id']),
                amount=p['amount'],
                user=current_user
            )

            payment.save()

        return JsonResponse({
            'success':True,
            'id':i.id,
            'date': f'{i.datetime.year}/{i.datetime.month}/{i.datetime.day} {i.datetime.hour}:{i.datetime.minute}'
        })