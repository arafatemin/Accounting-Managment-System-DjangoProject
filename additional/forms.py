from django.forms import ModelForm
from .models import *



class IncomeForm(ModelForm):
    class Meta:
        model = AdditionalIncomes
        exclude = ('user',)

class OutcomeForm(ModelForm):
    class Meta:
        model = AdditionalOutcomes
        exclude = ('user',)



class OutcomeCategoryForm(ModelForm):
    class Meta:
        model = OutcomeCategory
        exclude = ('user',)

class IncomeCategoryForm(ModelForm):
    class Meta:
        model = IncomeCategory
        exclude = ('user',)