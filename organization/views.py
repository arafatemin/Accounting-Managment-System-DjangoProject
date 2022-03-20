from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.forms import ModelForm
from django.contrib import messages
from django.views import View
from .models import Organization
from .models import City
from .forms import OrganizationForm
from customuser.models import CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from product_transfer.models import *
from bank.models import Bank


class OrgDebtForm(ModelForm):
    class Meta:
        model = OrgDebt
        exclude = ('user', 'organization')


@login_required(login_url='/login/')
def add_debt(request, id):
    current_user = get_object_or_404(CustomUser, username=request.user.username)
    org = get_object_or_404(Organization, id=id)
    form = OrgDebtForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = current_user
        obj.organization = org
        obj.save()
        messages.success(request, 'Debt has been added successfully')
    else:
        messages.error(request, str(form.errors))
    return redirect(reverse('single_organization', kwargs={'id': id}))


class AddOrganization(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            context = {
                'cities': City.objects.all()
            }
            return render(request, 'organizations/add_organization.html', context=context)

        return redirect(reverse('organizations'))

    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            form = OrganizationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Organization has been added successfully !')
                return redirect(reverse('organizations'))
            else:
                messages.error(request, str(form.errors))
        return redirect(reverse('add_organizations'))


@login_required(login_url='/login/')
def organizations(request, *args, **kwargs):
    current_user = get_object_or_404(CustomUser, username=request.user.username)
    context = {
        'organizations': Organization.objects.all(),
        'current_user': current_user,
    }
    return render(request, 'organizations/organization.html', context=context)


@login_required(login_url='/login/')
def single_organization(request, id, *args, **kwargs):
    current_user = get_object_or_404(CustomUser, username=request.user.username)
    current_org = current_user.organization
    org = get_object_or_404(Organization, id=id)
    transfers = ProductTransfer.objects.filter(from_org=current_org, to_org=org)
    p_payments = TransferPayment.objects.filter(transfer__from_org=current_org, transfer__to_org=org)
    d_payments = OrgDebtPayment.objects.filter(debt__organization=org)
    total = 0
    payed = 0
    total_payed_debt = 0
    for d in OrgDebtPayment.objects.filter(debt__organization=org): total_payed_debt += d.amount
    for p in TransferPayment.objects.filter(transfer__from_org=current_org, transfer__to_org=org): payed += p.amount
    for p in OrgDebtPayment.objects.filter(debt__organization=org): payed += p.amount
    for p in TransferedProduct.objects.filter(transfer__from_org=current_org, transfer__to_org=org): total = total + p.price + (p.price * p.transfer.tax.percent/100)
    for p in OrgDebt.objects.filter(organization=org): total += p.amount

    context = {
        'org': org,
        'users': CustomUser.objects.filter(organization=org),
        'transfers': transfers,
        'p_payments': p_payments,
        'd_payments': d_payments,
        'total': total,
        'paid': payed,
        'max': total - payed,
        'debts': OrgDebt.objects.filter(organization=org),
        'methods': Bank.objects.filter(organization=current_user.organization),
        'org_methods': Bank.objects.filter(organization=org),
        'total_payed_debt': total_payed_debt,
    }
    return render(request, 'organizations/single_organization.html', context=context)


@login_required(login_url='/login/')
def make_payment(request, id):
    org = get_object_or_404(Organization, id=id)
    transfers = ProductTransfer.objects.filter(to_org=org)
    debts = OrgDebt.objects.filter(organization=org)
    current_user = get_object_or_404(CustomUser, username=request.user.username)
    total_sar_payed = float(request.POST['amount'])
    type = request.POST['type']
    to_bank = get_object_or_404(Bank, id=request.POST['to_bank'])
    from_bank = get_object_or_404(Bank, id=request.POST['from_bank'])
    note = request.POST['note']
    t = total_sar_payed
    if type == "transfer":
        for p in transfers:
            if total_sar_payed > 0:
                pwu_total = 0
                for pwu in TransferedProduct.objects.filter(transfer=p):
                    pwu_total += pwu.price + (pwu.price*pwu.transfer.tax.percent/100)
                total_payed = 0
                for payed in TransferPayment.objects.filter(transfer=p):
                    total_payed += payed.amount

                debt = pwu_total - total_payed
                payable = 0
                if debt < total_sar_payed:
                    payable = debt
                else:
                    payable = total_sar_payed
                total_sar_payed -= payable
                p = TransferPayment(
                    transfer=p,
                    amount=payable,
                    from_bank=from_bank,
                    to_bank=to_bank,
                    user=current_user
                )
                p.save()

    elif type == "debt":
        for d in debts:
            if total_sar_payed > 0:
                total = 0
                total += d.amount

                total_payed = 0
                for payed in OrgDebtPayment.objects.filter(debt=d):
                    total_payed += payed.amount

                debt = total - total_payed
                payable = 0
                if debt < total_sar_payed:
                    payable = debt
                else:
                    payable = total_sar_payed
                total_sar_payed -= payable
                if payable > 0:
                    p = OrgDebtPayment(
                        debt=d,
                        to_bank=to_bank,
                        from_bank=from_bank,
                        amount=payable,
                        user=current_user,
                        note=note
                    )
                    p.save()
            else:
                pass
    else:
        pass
    if type == "transfer":
        messages.success(request, f'Totally Payed For Transfers{t - total_sar_payed} SAR')
    if type == "debt":
        messages.success(request, f'Totally Payed For Debt {t - total_sar_payed} SAR')

    return redirect(reverse('single_organization', kwargs={'id': id}))
