from .models import Vendor
from django.forms import ModelForm




class VendorForm(ModelForm):
    class Meta:
        exclude = ('belongs_to',)
        model = Vendor