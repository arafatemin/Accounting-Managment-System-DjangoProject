from django import template
from product_transfer.models import *
register = template.Library()



def minus(a,b): return  a - b



def pwus(transfer):
    s = ""
    p = TransferedProduct.objects.filter(transfer=transfer)
    for i in p:
        s += "<tr><td>"+i.product.product.name+"</td><td>"+str(i.unit)+ " "+i.product.product.type.name +"</td></tr>"
    return s

def pwu_debtpayment_debt(debt):
    total = 0
    debts = OrgDebt.objects.filter(organization=debt.debt.organization)
    for d in debts:
        total += d.amount
    return total


register.filter('pwus',pwus)
register.filter('pwu_debtpayment_debt',pwu_debtpayment_debt)



register.filter('minus',minus)
