from django.forms import ModelForm
from .models import Invoice







class InvoiceForm(ModelForm):
    class Meta:
        model = Invoice
        exclude = ('user', 'tax','customer')