from django.forms import ModelForm
from .models import Purchase,BoughtProduct,ReturnedProduct,Payment,Debt



class DebtForm(ModelForm):
    class Meta:
        model = Debt
        exclude = ('user','customer')


class PurchaseForm(ModelForm):
    class Meta:
        model = Purchase
        exclude = ('user','tax')


class BoughtProductForm(ModelForm):
    class Meta:
        model = BoughtProduct
        exclude = ('user',)

class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        exclude = ('user',)