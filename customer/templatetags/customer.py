from invoice.models import SoldProduct,Payment
from django import template
register = template.Library()



def minus(a,b): return  a - b

def calculate_debt(purchase):
    total = 0.0
    pwus = SoldProduct.objects.filter(invoice=purchase)
    for pwu in pwus:
        total += pwu.price
    total = total + (total * purchase.tax.percent / 100)

    payed = 0.0
    for payment in Payment.objects.filter(invoice=purchase):
        payed += payment.amount

    s = "Paid"
    s1 = "Partially paid"
    gap = total - payed

    if gap > 0:
        return f"<td style='color: red;'>{s1}</td><td style='color: red;'>{gap} SAR</td>"
    return f"<td style='color: green;'>{s}</td><td style='color: green;'>{gap} SAR</td>"


def pwus(invoice):
    s = ""
    p = SoldProduct.objects.filter(invoice=invoice)
    for i in p:
        s += "<tr><td>"+i.product.product.name+"</td><td>"+str(i.unit)+ " "+i.product.product.type.name +"</td></tr>"
    return s

register.filter('pwus',pwus)
register.filter('minus',minus)
register.filter('debt',calculate_debt)