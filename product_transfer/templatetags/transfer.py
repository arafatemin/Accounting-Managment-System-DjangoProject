from django import template
from ..models import *
register = template.Library()

def divide(a,b):return a/b
def minus(a,b):return  a - b

def calculate_debt(transfer):
    total = 0.0
    pwus = TransferedProduct.objects.filter(transfer=transfer)
    for pwu in pwus:
        total += pwu.price
    total = total + (total * transfer.tax.percent / 100)

    payed = 0.0
    for payment in TransferPayment.objects.filter(transfer=transfer):
        payed += payment.amount

    s = "Paid"
    s1 = "Partially paid"
    gap = total - payed
    gap = round(gap, 2)

    if gap > 0:
        return f"<td style='color: red;'>{gap} SAR</td><td style='color: red;'>{s1}</td>"
    return f"<td style='color: green;'>{gap} SAR</td><td style='color: green;'>{s}</td>"

def calculate_total(transfer):
    total = 0.0
    pwus = TransferedProduct.objects.filter(transfer=transfer)
    for pwu in pwus:
        total += pwu.price
    total = total + (total * transfer.tax.percent / 100)
    return total


def calculate_payed(transfer):

    payed = 0.0
    for payment in TransferPayment.objects.filter(transfer=transfer):
        payed += payment.amount
    return payed

def return_payment(transfer):
    p_payments = TransferPayment.objects.filter(transfer=transfer)
    return p_payments

register.filter('debt',calculate_debt)
register.filter('purchase_debt',calculate_debt)
register.filter('purchase_payed',calculate_payed)
register.filter('return_payment',return_payment)
register.filter('total',calculate_total)
register.filter('divide',divide)
register.filter('minus',minus)