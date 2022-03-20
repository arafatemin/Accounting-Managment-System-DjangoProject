from django.forms import ModelForm
from .models import UnitType,ProductCategory,Product,BaseProduct


class UnitTypeForm(ModelForm):
    class Meta:
        fields = '__all__'
        model = UnitType


class ProductCategoryForm(ModelForm):
    class Meta:
        fields = '__all__'
        model = ProductCategory


class BaseProductForm(ModelForm):
    class Meta:
        fields = '__all__'
        model = BaseProduct



class ProductForm(ModelForm):
    class Meta:
        fields = '__all__'
        model = Product
        exclude = ('organization',)

class ProductsForm(ModelForm):
    class Meta:
        fields = '__all__'
        model = Product
        exclude = ('organization','product')