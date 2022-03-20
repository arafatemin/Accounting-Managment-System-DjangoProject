from purchase.models import Purchase,BoughtProduct,Debt
from django import template
register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg


def pwus(purchase):
    s = ""
    p = BoughtProduct.objects.filter(purchase=purchase)
    for i in p:
        s += "<tr><td>"+i.product.product.name+"</td><td>"+str(i.unit)+ " "+i.product.product.type.name +"</td></tr>"
    return s

def pwu_debtpayment_debt(debt):
    total = 0
    debts = Debt.objects.filter(customer=debt.debt.customer)
    for d in debts:
        total += d.amount
    return total


register.filter('pwus',pwus)
register.filter('pwu_debtpayment_debt',pwu_debtpayment_debt)

