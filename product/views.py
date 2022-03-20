from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views import View
from customuser.models import CustomUser
from .models import UnitType, ProductCategory, BaseProduct, Product
from django.contrib import messages
from .form import UnitTypeForm, ProductCategoryForm, BaseProductForm, ProductForm, ProductsForm
from organization.models import Organization
from itertools import chain
from product_transfer.models import TransferedProduct
from invoice.models import SoldProduct
from purchase.models import BoughtProduct
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from returnproduct.models import ReturnWithUnit
from fromstock.models import ProductWithUnit
import datetime
from product.templatetags.product import cpu


def get_date(i):
    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        return now - i.date
    except:
        return now - i.datetime




@login_required(login_url='/login/')
def product_detail(request, id, *args, **kwargs):
    current_user = get_object_or_404(CustomUser, username=request.user.username)
    # products = get_object_or_404(Product, product_id=id)
    context = {
        'product': get_object_or_404(BaseProduct, id=id),
        # 'products': products,
        'org': current_user.organization,
        'orgs': Organization.objects.all(),

    }
    transfer = TransferedProduct.objects.filter(product__product=context['product'])
    transfer.filter((Q(transfer__from_org=current_user.organization) | Q(transfer__to_org=current_user.organization)))
    sold = SoldProduct.objects.filter(product__product=context['product'], user__organization=current_user.organization)
    bought = BoughtProduct.objects.filter(product__product=context['product'],
                                          user__organization=current_user.organization)

    returned = ReturnWithUnit.objects.filter(product__product=context['product'],
                                             user__organization=current_user.organization)
    stock = ProductWithUnit.objects.filter(product__product=context['product'],
                                           user__organization=current_user.organization)

    result_list = sorted(chain(transfer, sold, bought, stock, returned), key=get_date)

    context['history'] = result_list
    obj = Product.objects.filter(organization=context['org'], product=context['product'])
    if obj.count() > 0:
        context['productt'] = obj[0]
    return render(request, template_name='product/single_product.html', context=context)


@login_required(login_url='/login/')
def update_product(request, id, *args, **kwargs):
    product = get_object_or_404(BaseProduct, id=id)
    context = {
        'product': product,
        'product_category': ProductCategory.objects.all(),
        'unit_type': UnitType.objects.all(),
    }
    if request.method == 'POST':
        form = BaseProductForm(request.POST or None, request.FILES or None, instance=product)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            messages.success(request, 'Product updated successfully!')
            return redirect(reverse('product_detail', kwargs={"id": product.id}))
        else:
            messages.error(request, str(form.errors))
    return render(request, template_name='product/update_product.html', context=context)


@login_required(login_url='/login/')
def import_product(request, *args, **kwargs):
    if request.method == 'POST':
        form = ProductForm(request.POST or None)
        if form.is_valid():
            obj = form.save(commit=False)
            org = get_object_or_404(CustomUser, username=request.user.username).organization
            if Product.objects.filter(organization=org, product=obj.product).count() > 0:
                messages.error(request, 'You already imported this product')
            else:
                obj.organization = org
                obj.save()
                messages.success(request, 'Product imported successfully!')
        else:
            messages.error(request, str(form.errors))

    return redirect(reverse('products'))


class ProductView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        products = BaseProduct.objects.all()
        productss = Product.objects.filter(organization=current_org)
        _category = request.GET.get('_category')
        _sku = request.GET.get('_sku')

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

        if _category:
            products = BaseProduct.objects.filter(category_id=_category)
            productss = Product.objects.filter(product__category_id=_category, organization=current_org)
            page_number = request.GET.get('page', 1)
            paginator = Paginator(products, 15)

            # prices = 0
            #
            # for p in productss:
            #     prices += p.price * cpu(p.product, current_org)

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
            context = {
                'page_obj': page_obj,
                'org': get_object_or_404(CustomUser, username=request.user.username).organization,
                'units': UnitType.objects.all(),
                'product_categories': ProductCategory.objects.all(),
                # 'total_price': prices

            }
            return render(request, 'product/products.html', context=context)

        elif _sku:
            products = BaseProduct.objects.filter(id=_sku)
            productss = Product.objects.filter(product__id=_sku, organization=current_org)
            page_number = request.GET.get('page', 1)
            paginator = Paginator(products, 15)

            prices = 0

            for p in productss:
                prices += p.price * cpu(p.product, current_org)

            try:
                page_obj = paginator.get_page(page_number)  # returns the desired page object
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
            context = {
                'page_obj': page_obj,
                'org': get_object_or_404(CustomUser, username=request.user.username).organization,
                'units': UnitType.objects.all(),
                'product_categories': ProductCategory.objects.all(),


            }
            return render(request, 'product/products.html', context=context)

        context = {'page_range': page_range, 'total_pages': total_pages,
                   'org': get_object_or_404(CustomUser, username=request.user.username).organization,
                   'units': UnitType.objects.all(), 'product_categories': ProductCategory.objects.all(),
                   'products': products,
                   'page_obj': page_obj,
                   }

        return render(request, 'product/products.html', context=context)

    def post(self, request, *args, **kwargs):
        form = BaseProductForm(request.POST or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            messages.success(request, message=f'<strong>{obj.name}</strong> has been added successfully!')
        else:
            messages.error(request, message=str(form.errors))

        return redirect(reverse('products'))


@login_required(login_url='/login/')
def update_products(request, id, *args, **kwargs):
    user = get_object_or_404(CustomUser, username=request.user.username)

    product = get_object_or_404(Product, id=id)

    # product_product = get_object_or_404(BaseProduct,id=product.id)

    context = {
        'product': product,
        # 'product_product': product_product,
        'product_category': ProductCategory.objects.all(),
        'unit_type': UnitType.objects.all(),
    }
    if request.method == 'POST':
        form = ProductsForm(request.POST or None, instance=product)
        if form.is_valid():
            obj = form.save(commit=False)
            # obj.product = product_product
            # obj.organization = user.organization
            obj.save()
            messages.success(request, 'Product updated successfully!')
            return redirect(reverse('product_detail', kwargs={"id": product.product.id}))
        else:
            messages.error(request, str(form.errors))
    return render(request, template_name='product/update_products.html', context=context)


class ProductCategoryView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        context = {
            'product_categories': ProductCategory.objects.all()
        }
        return render(request, 'product/product_category.html', context=context)

    def post(self, request, *args, **kwargs):
        form = ProductCategoryForm(request.POST or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            messages.success(request, message=f'<strong>{obj.title}</strong> has been saved successfully!')
        else:
            messages.error(request, message=str(form.errors))

        return redirect(reverse('product_category'))


class UnitTypeView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        context = {
            'unit_types': UnitType.objects.all()
        }
        return render(request, 'product/unit_type.html', context=context)

    def post(self, request, *args, **kwargs):
        form = UnitTypeForm(request.POST or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            messages.success(request, message=f'<strong>{obj.name}</strong> has been saved successfully!')
        else:
            print(form.errors)
            messages.error(request, message=str(form.errors))

        return redirect(reverse('unit_type'))
