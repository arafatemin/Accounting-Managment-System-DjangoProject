from django import template
register = template.Library()
from ..models import BoughtProduct,Payment


def divide(a,b):return a/b
def minus(a,b):return  a - b

def calculate_debt(purchase):
    total = 0.0
    pwus = BoughtProduct.objects.filter(purchase=purchase)
    for pwu in pwus:
        total += pwu.price
    total = total + (total * purchase.tax.percent / 100)

    payed = 0.0
    for payment in Payment.objects.filter(purchase=purchase):
        payed += payment.amount

    s = "Paid"
    s1 = "Partially paid"
    gap = total - payed

    if gap > 0:
        return f"<td style='color: red;'>{gap} SAR</td><td style='color: red;'>{s1}</td>"
    return f"<td style='color: green;'>{gap} SAR</td><td style='color: green;'>{s}</td>"

def calculate_total(purchase):
    total = 0.0
    pwus = BoughtProduct.objects.filter(purchase=purchase)
    for pwu in pwus:
        total += pwu.price
    total = total + (total * purchase.tax.percent / 100)
    return total


def calculate_payed(purchase):

    payed = 0.0
    for payment in Payment.objects.filter(purchase=purchase):
        payed += payment.amount
    return payed

def return_payment(purchase):
    p_payments = Payment.objects.filter(purchase=purchase)


    return p_payments

register.filter('debt',calculate_debt)
register.filter('purchase_debt',calculate_debt)
register.filter('purchase_payed',calculate_payed)
register.filter('return_payment',return_payment)
register.filter('total',calculate_total)
register.filter('divide',divide)
register.filter('minus',minus)