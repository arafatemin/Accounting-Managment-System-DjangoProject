from django.forms import ModelForm
from .models import ProductInStock




class StockForm(ModelForm):
    class Meta:
        model=ProductInStock
        exclude = ('')