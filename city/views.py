from django.shortcuts import render,redirect
from django.views import View
from django.forms import ModelForm
from .models import City
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

class CityForm(ModelForm):
    class Meta:
        model = City
        exclude=[]



class Cities(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = ''
    def get(self,request,*args,**kwargs):
        context = {
            'cities':City.objects.all()
        }
        return render(request,'city/cities.html',context=context)


    def post(self,request,*args,**kwargs):
        form = CityForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            messages.success(request,f'<strong>{obj.name}</strong> has been added successfully !')
        else:
            messages.error(request,str(form.errors))

        return redirect('cities')