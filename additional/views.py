from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views import View
from .models import *
from django.contrib import messages
from .forms import OutcomeCategoryForm
from customuser.models import CustomUser
from bank.models import Bank
from .forms import *
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin


class OutcomeCategoryView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        context = {
            'outcome_categories': OutcomeCategory.objects.filter(user__organization=current_user.organization)
        }
        return render(request, 'additional/outcome_category.html', context=context)

    def post(self, request, *args, **kwargs):
        form = OutcomeCategoryForm(request.POST or None)
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = current_user
            obj.save()
            messages.success(request, message=f'<strong>{obj.name}</strong> has been saved successfully!')
        else:
            messages.error(request, message=str(form.errors))

        return redirect(reverse('outcome_category'))




class IncomeCategoryView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        context = {
            'income_categories': IncomeCategory.objects.filter(user__organization=current_user.organization)
        }
        return render(request, 'additional/income_category.html', context=context)

    def post(self, request, *args, **kwargs):
        form = IncomeCategoryForm(request.POST or None)
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = current_user
            obj.save()
            messages.success(request, message=f'<strong>{obj.name}</strong> has been saved successfully!')
        else:
            messages.error(request, message=str(form.errors))

        return redirect(reverse('income_category'))


class OutcomeView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        outcome_categories = OutcomeCategory.objects.filter(user__organization=current_user.organization)
        banks = Bank.objects.filter(organization=current_user.organization)
        outcomes = AdditionalOutcomes.objects.filter(user__organization=current_user.organization)
        context = {
            'outcome_categories': outcome_categories,
            'banks': banks,
            'outcomes': outcomes
        }

        if 'outcome' in request.GET:
            outcome_id = int(request.GET['outcome'])
            if outcome_id >= 0:
                outcomes = outcomes.filter(category_id=outcome_id)
                context['outcome_id'] = outcome_id

        if 'from' in request.GET:
            time = request.GET['from'].split('/')
            if len(time) == 3:
                t = datetime(int(time[2]), int(time[1]), int(time[0]))
                outcomes = outcomes.filter(datetime__gte=t)
                context['from'] = request.GET['from']

            # time = datetime()

        if 'to' in request.GET:
            time = request.GET['to'].split('/')
            if len(time) == 3:
                t = datetime(int(time[2]), int(time[1]), int(time[0]))
                outcomes = outcomes.filter(datetime__lte=t)
                context['to'] = request.GET['to']

        return render(request, 'additional/outcome.html', context)

    def post(self, request, *args, **kwargs):
        form = OutcomeForm(request.POST)
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = current_user
            obj.save()
            messages.success(request, message=f'Outcome has been saved successfully!')
        else:
            messages.error(request, message=str(form.errors))
        return redirect(reverse('outcome'))


class IncomeView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        banks = Bank.objects.filter(organization=current_user.organization)
        outcomes = AdditionalIncomes.objects.filter(user__organization=current_user.organization)
        income_categories = IncomeCategory.objects.all()
        context = {
            'banks': banks,
            'incomes': outcomes,
            'income_categories': income_categories,
        }
        return render(request, 'additional/income.html', context)

    def post(self, request, *args, **kwargs):
        form = IncomeForm(request.POST)
        current_user = get_object_or_404(CustomUser, username=request.user.username)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = current_user
            obj.save()
            messages.success(request, message=f'Income has been saved successfully!')
        else:
            messages.error(request, message=str(form.errors))
        return redirect(reverse('income'))
