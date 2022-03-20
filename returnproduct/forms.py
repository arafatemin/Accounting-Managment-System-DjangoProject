from django.forms import ModelForm
from .models import *




class ReturnForm(ModelForm):
    class Meta:
        model = Return
        exclude = ('user','customer')

class ReturnPaymentForm(ModelForm):
    class Meta:
        model = ReturnPayment
        exclude = ('user','returned')