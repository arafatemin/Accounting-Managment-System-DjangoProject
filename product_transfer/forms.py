from django.forms import ModelForm
from .models import ProductTransfer



class TransferForm(ModelForm):
    class Meta:
        model = ProductTransfer
        exclude = ('user', 'tax','from_org')