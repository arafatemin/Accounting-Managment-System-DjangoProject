from django.shortcuts import render, get_object_or_404, redirect, reverse
from customuser.models import CustomUser
from django.views import View
from django.forms import ModelForm
from .models import *
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from product.models import Product
from product.templatetags.product import cpu
from invoice.models import Payment as InvoicePayment
from additional.models import AdditionalIncomes, AdditionalOutcomes
from bank.models import *
from purchase.models import Payment as PurchasePayment
from purchase.models import DebtPayment
from purchase.models import DebtPayment
from product_transfer.models import *
from returnproduct.models import ReturnPayment


class BankForm(ModelForm):
    class Meta:
        model = Bank
        exclude = ('organization',)


class TransferForm(ModelForm):
    class Meta:
        model = Transfer
        exclude = ('user',)


@login_required(login_url='/login/')
def single_bank(request, id):
    current_org = get_object_or_404(CustomUser, username=request.user.username).organization
    account = get_object_or_404(Bank, id=id)

    # incomes
    invoice_payment = 0
    for i in InvoicePayment.objects.filter(bank=account): invoice_payment += i.amount

    money_transfer_in = 0
    for i in Transfer.objects.filter(to_account=account): money_transfer_in += i.amount

    org_debt_payment_in = 0
    for i in OrgDebtPayment.objects.filter(to_bank=account): org_debt_payment_in += i.amount

    product_transfer_payment_in = 0
    for i in TransferPayment.objects.filter(to_bank=account): product_transfer_payment_in += i.amount

    additional_income = 0
    for i in AdditionalIncomes.objects.filter(bank=account): additional_income += i.amount

    # outcomes

    purchase_payment = 0
    for i in PurchasePayment.objects.filter(bank=account): purchase_payment += i.amount

    money_transfer_out = 0
    for i in Transfer.objects.filter(from_account=account): money_transfer_out += i.amount

    org_debt_payment_out = 0
    for i in OrgDebtPayment.objects.filter(from_bank=account): org_debt_payment_out += i.amount

    product_transfer_payment_out = 0
    for i in TransferPayment.objects.filter(from_bank=account): product_transfer_payment_out += i.amount

    vendor_debt_payment = 0
    for i in DebtPayment.objects.filter(bank=account): vendor_debt_payment += i.amount

    additional_outcome = 0
    for i in AdditionalOutcomes.objects.filter(bank=account): additional_outcome += i.amount

    return_payment = 0
    for i in ReturnPayment.objects.filter(bank=account): return_payment += i.amount

    context = {
        "account": account,
        "org": current_org,
        "invoice_payment": invoice_payment,
        "money_transfer_in": money_transfer_in,
        "org_debt_payment_in": org_debt_payment_in,
        "product_transfer_payment": product_transfer_payment_in,
        "additional_income": additional_income,

        "vendor_debt_payment": vendor_debt_payment,
        "product_transfer_payment_out": product_transfer_payment_out,
        "org_debt_payment_out": org_debt_payment_out,
        "money_transfer_out": money_transfer_out,
        "purchase_payment": purchase_payment,
        "additional_outcome": additional_outcome,
        "return_payment": return_payment,
    }
    return render(request, 'bank/single_bank.html', context=context)


class Banks(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        banks = Bank.objects.filter(organization=current_org)

        context = {
            "org": current_org,
            'banks': Bank.objects.filter(organization=current_org),
        }
        return render(request, 'bank/banks.html', context=context)

    def post(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        form = BankForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.organization = current_org
            obj.save()
            messages.success(request, f'<strong>{obj.name}</strong> has been added successfully !')
        else:
            messages.error(request, str(form.errors))

        return redirect('banks')


class TransferMoney(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        banks = Bank.objects.filter(organization=current_user.organization)
        bankss = Bank.objects.all()
        transfers = Transfer.objects.filter(Q(from_account__organization=current_user.organization) | Q(
            to_account__organization=current_user.organization))

        transfers_out = Transfer.objects.filter(from_account__organization=current_user.organization)
        transfers_in = Transfer.objects.filter(to_account__organization=current_user.organization)

        out_total = 0
        in_total = 0

        for o in transfers_out:
            out_total += o.amount

        for i in transfers_in:
            in_total += i.amount

        context = {
            'org': current_user.organization,
            'banks': banks,
            'bankss': bankss,
            'transfers': transfers,
            'out_total': out_total,
            'in_total': in_total,
        }

        return render(request, 'transfer_money.html', context)

    def post(self, request, *args, **kwargs):
        form = TransferForm(request.POST)
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = current_user
            obj.save()
            messages.success(request, message=f'Money Has Been Transferred')
        else:
            messages.error(request, message=str(form.errors))
        return redirect(reverse('transfer_money'))
