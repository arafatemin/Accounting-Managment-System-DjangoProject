from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views import View
from .models import Vendor
from customuser.models import CustomUser
from .form import VendorForm
from django.contrib import messages
from purchase.models import Purchase, Payment, BoughtProduct
from bank.models import Bank
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from purchase.models import Debt, DebtPayment
from purchase.forms import DebtForm

@login_required(login_url='/login/')

def add_debt(request, id):
    current_user = get_object_or_404(CustomUser, username=request.user.username)
    vendor = get_object_or_404(Vendor, id=id)
    form = DebtForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = current_user
        obj.customer = vendor
        obj.save()
        messages.success(request, 'Debt has been added successfully')
    else:
        messages.error(request, str(form.errors))
    return redirect(reverse('single_vendor', kwargs={'id': id}))


@login_required(login_url='/login/')
def single_vendor(request, id):
    vendor = get_object_or_404(Vendor, id=id)
    purchases = Purchase.objects.filter(customer=vendor)
    current_user = get_object_or_404(CustomUser, username=request.user.username)
    p_payments = Payment.objects.filter(purchase__customer=vendor)
    d_payments = DebtPayment.objects.filter(debt__customer=vendor)
    total = 0
    payed = 0
    total_payed_debt = 0
    for d in DebtPayment.objects.filter(debt__customer=vendor):
        total_payed_debt += d.amount
    for p in Payment.objects.filter(purchase__customer=vendor): payed += p.amount
    for p in DebtPayment.objects.filter(debt__customer=vendor): payed += p.amount
    for p in BoughtProduct.objects.filter(purchase__customer=vendor): total += p.price
    for p in Debt.objects.filter(customer=vendor): total += p.amount
    context = {
        'object': vendor,
        'purchases': purchases,
        'p_payments': p_payments,
        'd_payments': d_payments,
        'total': total,
        'paid': payed,
        'max': total - payed,
        'debts': Debt.objects.filter(customer=vendor),
        'methods': Bank.objects.filter(organization=current_user.organization),
        'total_payed_debt': total_payed_debt
    }
    return render(request, 'vendors/single_vendor.html', context=context)

@login_required(login_url='/login/')
def make_payment(request, id):
    vendor = get_object_or_404(Vendor, id=id)
    purchases = Purchase.objects.filter(customer=vendor)
    debts = Debt.objects.filter(customer=vendor)
    current_user = get_object_or_404(CustomUser, username=request.user.username)
    total_sar_payed = float(request.POST['amount'])
    type = request.POST['type']
    bank = get_object_or_404(Bank, id=request.POST['bank'])
    note = request.POST['note']
    t = total_sar_payed

    if type == "purchase":
        for p in purchases:
            if total_sar_payed > 0:
                pwu_total = 0
                for pwu in BoughtProduct.objects.filter(purchase=p):
                    pwu_total += pwu.price
                total_payed = 0
                for payed in Payment.objects.filter(purchase=p):
                    total_payed += payed.amount

                debt = pwu_total - total_payed
                payable = 0
                if debt < total_sar_payed:
                    payable = debt
                else:
                    payable = total_sar_payed
                total_sar_payed -= payable
                if payable > 0:
                    p = Payment(
                        purchase=p,
                        bank=bank,
                        amount=payable,
                        user=current_user
                    )
                    p.save()

    elif type == "debt":
        for d in debts:
            if total_sar_payed > 0:
                total = 0
                total += d.amount

                total_payed = 0
                for payed in DebtPayment.objects.filter(debt=d):
                    total_payed += payed.amount

                debt = total - total_payed
                payable = 0
                if debt < total_sar_payed:
                    payable = debt
                else:
                    payable = total_sar_payed
                total_sar_payed -= payable
                if payable > 0:
                    p = DebtPayment(
                        debt=d,
                        bank=bank,
                        amount=payable,
                        user=current_user,
                        note=note
                    )
                    p.save()
            else:
                pass
    else:
        pass
    if type == "purchase":
        messages.success(request, f'Totally Payed For Purchases{t - total_sar_payed} SAR')
    if type == "debt":
        messages.success(request, f'Totally Payed For Debt {t - total_sar_payed} SAR')

    return redirect(reverse('single_vendor', kwargs={'id': id}))


class VendorView(View):
    def get(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        context = {
            'vendors': Vendor.objects.filter(belongs_to=current_org)
        }
        return render(request, 'vendors/vendors.html', context=context)

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

        return redirect(reverse('vendors'))
