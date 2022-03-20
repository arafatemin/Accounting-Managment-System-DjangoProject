from django.db.models import Sum
from django.template import Library

from customuser.models import CustomUser
from product.models import Product
from django.shortcuts import reverse, get_object_or_404
from product.templatetags.product import cpu
from invoice.models import Payment as InvoicePayment
from additional.models import AdditionalIncomes, AdditionalOutcomes
from bank.models import *
from purchase.models import Payment as PurchasePayment
from purchase.models import DebtPayment
from product_transfer.models import *
from datetime import datetime
from django import template
from django.db.models import Sum, Avg, Max, Min, Count

register = template.Library()


@register.filter
def sum(queryset, field):
    return queryset.aggregate(sum_value=Sum(field)).get('sum_value')


@register.filter
def avg(queryset, field):
    return queryset.aggregate(avg_value=Avg(field)).get('avg_value')


@register.filter
def min(queryset, field):
    return queryset.aggregate(min_value=Min(field)).get('min_value')


@register.filter
def max(queryset, field):
    return queryset.aggregate(max_value=Max(field)).get('max_value')


@register.filter
def count(queryset, field):
    return queryset.aggregate(count_value=Count(field)).get('count_value')


def minus(a, b):
    if a and b:
        return a - b
    else:
        pass



def products_in_organization(org):
    result = ""
    products = Product.objects.filter(organization=org)
    for p in products:
        url = reverse('product_detail', kwargs={'id': p.product.id})
        unit = cpu(p.product, org)
        total = p.price * unit
        total = round(total, 2)
        result += f"<tr>" \
                  f"<td><a href='{url}'>{p.product.sku} --- {p.product.name}</a></td>" \
                  f"<td>{unit} {p.product.type}</td>" \
                  f"<td>{p.price} SAR</td>" \
                  f"<td>{p.sell_price} SAR</td>" \
                  f"<td>{total} SAR</td>" \
                  f"</tr>"
    return result


def organization_product_price(org):
    products = Product.objects.filter(organization=org)
    grand_total = 0
    for p in products:
        unit = cpu(p.product, org)
        total = p.price * unit
        grand_total += total
    return grand_total


def organization_balance(org):
    def get_tr(account, income, outcome, total):
        income = round(income, 2)
        outcome = round(outcome, 2)
        total = round(total, 2)
        s = f"""<tr>
                                            <td>{account}</td>
                                            <td style="color: green">{income} SAR</td>
                                            <td style="color: red">{outcome} SAR</td>
                                        """

        if total < 0:
            s += f'<td style="color: red">{total} SAR</td></tr>'
        else:
            s += f'<td style="color: green">{total} SAR</td></tr>'
        return s

    s = ''
    g_income = 0
    g_outcome = 0
    for bank in Bank.objects.filter(organization=org):
        income_total = 0
        outcome_total = 0
        invoice_payment = InvoicePayment.objects.filter(user__organization=org, bank=bank)
        incomes = AdditionalIncomes.objects.filter(user__organization=org, bank=bank)
        outcomes = AdditionalOutcomes.objects.filter(user__organization=org, bank=bank)
        purchases = PurchasePayment.objects.filter(user__organization=org, bank=bank)
        money_out = Transfer.objects.filter(from_account__organization=org)
        money_in = Transfer.objects.filter(to_account__organization=org)
        vendor_payment = DebtPayment.objects.filter(user__organization=org, bank=bank)
        product_transfer = TransferPayment.objects.filter(user__organization=org, bank=bank)
        org_payment_out = OrgDebtPayment.objects.filter(user__organization=org, bank=bank)
        org_payment_in = OrgDebtPayment.objects.filter(debt__organization=org, bank=bank)
        for i in invoice_payment: income_total += i.amount
        for i in incomes: income_total += i.amount
        for i in outcomes: outcome_total += i.amount
        for i in purchases: outcome_total += i.amount
        for i in money_out: outcome_total += i.amount
        for i in vendor_payment: outcome_total += i.amount
        for i in org_payment_out: outcome_total += i.amount

        for i in org_payment_in: income_total += i.amount
        for i in money_in: income_total += i.amount
        g_income += income_total
        g_outcome += outcome_total
        s += get_tr(bank.name, income_total, outcome_total, income_total - outcome_total)

    return s + get_tr('', g_income, g_outcome, g_income - g_outcome)


def outcome_category_total(category, request):
    current_org = get_object_or_404(CustomUser, username=request.user.username).organization
    total = AdditionalOutcomes.objects.filter(user__organization=current_org, category=category)

    if 'from' in request.GET:
        time = request.GET['from'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            total = total.filter(datetime__gte=t)

    if 'to' in request.GET:
        time = request.GET['to'].split('/')
        if len(time) == 3:
            t = datetime(int(time[2]), int(time[1]), int(time[0]))
            total = total.filter(datetime__lte=t)

    return total.aggregate(
        Sum('amount'))["amount__sum"]


register = Library()
register.filter('minus', minus)
register.filter('balance', organization_balance)
register.filter('abs_sum', organization_product_price)
register.filter('products_in_organization', products_in_organization)
register.filter('outcome_category_total', outcome_category_total)
