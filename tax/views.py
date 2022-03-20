from django.shortcuts import render,redirect,reverse
from django.views import View
from .forms import TaxForm
from django.contrib import messages
from .models import Tax
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required



class TaxView(View):
    def get(self,request,*args,**kwargs):
        context = {
            'taxes':Tax.objects.all()
        }
        return render(request,'tax/tax.html',context=context)


    def post(self,request,*args,**kwargs):
        form = TaxForm(request.POST or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            messages.success(request,message=f'<strong>{obj.percent}</strong> has been saved successfully!')
        else:
            print(form.errors)
            messages.error(request,message=str(form.errors))

        return redirect(reverse('tax'))