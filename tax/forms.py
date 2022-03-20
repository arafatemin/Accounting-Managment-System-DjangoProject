from .models import Tax
from django.forms import ModelForm




class TaxForm(ModelForm):
    class Meta:
        model = Tax
        fields = '__all__'