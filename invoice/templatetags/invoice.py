from django import template
import arabic_reshaper
from PIL import ImageFont
from bidi.algorithm import get_display
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from bidi.algorithm import get_display
from AMS.settings import STATIC_ROOT
from ..models import SoldProduct,Payment

register = template.Library()


def divide(a,b):return a/b
def multiply(a,b):return a*b
def minus(a,b):return  a - b

def calculate_debt(invoice):
    total = 0.0
    pwus = SoldProduct.objects.filter(invoice=invoice)
    for pwu in pwus:
        total += pwu.price
    total = total + (total * invoice.tax.percent / 100)
    total = round(total, 2)
    payed = 0.0
    for payment in Payment.objects.filter(invoice=invoice):
        payed += payment.amount
        payed = round(payed, 2)

    s = "Paid"
    s1 = "Partially paid"
    gap = total - payed
    gap = round(gap, 2)
    if gap > 0:
        return f"<td style='color: red;'>{s1}</td><td style='color: red;'>{gap} SAR</td>"
    return f"<td style='color: green;'>{s}</td><td style='color: green;'>{gap} SAR</td>"

def calculate_payed(invoice):
    payed = 0.0
    for payment in Payment.objects.filter(invoice=invoice):
        payed += payment.amount
        payed = round(payed, 2)
    return payed

def arbic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

register.filter('arabic',arbic_text)

register.filter('debt',calculate_debt)
register.filter('payed',calculate_payed)
register.filter('invoice_debt',calculate_debt)

register.filter('divide',divide)
register.filter('multiply',multiply)
register.filter('minus',minus)