from django.shortcuts import render, reverse, redirect, get_object_or_404
from customuser.models import CustomUser
from django.views import View
from .models import Customer
from .forms import VendorForm
from django.contrib import messages
from invoice.models import Invoice, SoldProduct, Payment
from bank.models import Bank
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


@login_required(login_url='/login/')
def make_payment(request, id):
    customer = get_object_or_404(Customer, id=id)
    purchases = Invoice.objects.filter(customer=customer)
    current_user = get_object_or_404(CustomUser, username=request.user.username)
    if 'amount' in request.POST:
        total_sar_payed = float(request.POST['amount'])
        bank = get_object_or_404(Bank, id=request.POST['method'])
    else:
        total_sar_payed=False
        bank = False

    t = total_sar_payed
    for p in purchases:
        if total_sar_payed > 0:
            pwu_total = 0
            for pwu in SoldProduct.objects.filter(invoice=p):
                pwu_total += pwu.price + (pwu.invoice.tax.percent*pwu.price/100)
            total_payed = 0
            for payed in Payment.objects.filter(invoice=p):
                total_payed += payed.amount

            debt = pwu_total - total_payed
            payable = 0
            if debt < total_sar_payed:
                payable = debt
            else:
                payable = total_sar_payed
            total_sar_payed -= payable
            p = Payment(
                invoice=p,
                bank=bank,
                amount=payable,
                user=current_user
            )
            p.save()
    messages.success(request, f'Totally payed {t - total_sar_payed} SAR')
    return redirect(reverse('single_customer', kwargs={'id': id}))


@login_required(login_url='/login/')
def single_customer(request, id, *args, **kwargs):
    customer = get_object_or_404(Customer, id=id)
    purchases = Invoice.objects.filter(customer=customer)
    current_user = get_object_or_404(CustomUser, username=request.user.username)
    total = 0
    payed = 0
    for p in Payment.objects.filter(invoice__customer=customer): payed += p.amount
    for p in SoldProduct.objects.filter(invoice__customer=customer): total = total + p.price + (p.price * p.invoice.tax.percent) / 100

    context = {
        'object': customer,
        'purchases': purchases,
        'total': total,
        'paid': payed,
        'max': total - payed,
        'methods': Bank.objects.filter(organization=current_user.organization)
    }
    return render(request, 'customer/single_customer.html', context=context)


class CustomerView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        context = {
            'vendors': Customer.objects.filter(belongs_to=current_org)
        }
        return render(request, 'customer/customers.html', context=context)

    def post(self, request, *args, **kwargs):
        form = VendorForm(request.POST or None)
        if form.is_valid():
            current_org = get_object_or_404(CustomUser, username=request.user.username).organization
            obj = form.save(commit=False)
            obj.belongs_to = current_org
            obj.save()
            messages.success(request, f'<strong>{obj.name} </strong> has been added successfully!')
        else:
            messages.error(request, str(form.errors))
        if request.build_absolute_uri() == "invoice/add/":
            return redirect(reverse('add_invoice'))
        return redirect(reverse('add_invoice'))


def update_customer(request,id):
    customer = get_object_or_404(Customer,id=id)
    context = {
        'customer':customer
    }

    if request.method == 'POST':
        form = VendorForm(request.POST or None, instance=customer)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            messages.success(request, 'Customer updated successfully!')
        else:
            messages.error(request, str(form.errors))

        return redirect(reverse('customers'))
    return render(request, template_name='customer/update_customer.html', context=context)