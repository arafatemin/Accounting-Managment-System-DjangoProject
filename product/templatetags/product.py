from django import template
from invoice.models import SoldProduct, ReturnedProduct
from purchase.models import BoughtProduct
from purchase.models import ReturnedProduct as PurchaseBoughtProducts
from product.models import Product, BaseProduct
from product_transfer.models import TransferedProduct, TransferReturnedProduct
from fromstock.models import ProductWithUnit
from returnproduct.models import ReturnWithUnit

register = template.Library()


def divide(a, b):
    return a / b


def get_product_buy_sell_price(product, org):
    objs = Product.objects.filter(product=product, organization=org)
    if objs.count() > 0:
        return "<td>{0} SAR</td><td>{1} SAR</td>".format(objs[0].price, objs[0].sell_price)
    return "<td>You have not imported this product yet</td><td></td>"


def cpu(product, org):
    total = 0

    for p in SoldProduct.objects.filter(product__product=product, user__organization=org):
        if ReturnedProduct.objects.filter(sold_product=p).count() == 0:
            total -= p.unit

    for p in BoughtProduct.objects.filter(product__product=product, user__organization=org):
        if PurchaseBoughtProducts.objects.filter(bought_product=p).count() == 0:
            total += p.unit

    for p in TransferedProduct.objects.filter(product__product=product, transfer__from_org=org):
        if TransferReturnedProduct.objects.filter(product=p).count() == 0:
            total -= p.unit

    for p in TransferedProduct.objects.filter(product__product=product, transfer__to_org=org):
        if TransferReturnedProduct.objects.filter(product=p).count() == 0:
            total += p.unit

    for p in ProductWithUnit.objects.filter(product__product=product, user__organization=org):
        total += p.unit

    for p in ReturnWithUnit.objects.filter(product__product=product, user__organization=org):
        total += p.unit


    return total


register.filter('cpu', cpu)
register.filter('buy_sell_price', get_product_buy_sell_price)
register.filter('divide', divide)
