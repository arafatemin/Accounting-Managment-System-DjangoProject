from urllib import request

from django import template
from django.shortcuts import get_object_or_404
from django.urls import translate_url
from datetime import datetime, timedelta, time

from additional.models import AdditionalOutcomes
from customuser.models import CustomUser

register = template.Library()


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def outcome(category, request):
    current_org = get_object_or_404(CustomUser, username=request.user.username).organization

    today = datetime.now().date()
    tomorrow = today + timedelta(1)
    today_start = datetime.combine(today, time())
    today_end = datetime.combine(tomorrow, time())

    outcomes = AdditionalOutcomes.objects.filter(category=category, datetime__range=[today_start, today_end],
                                                 user__organization=current_org)

    amount = 0
    for o in outcomes:
        amount += o.amount

    return amount
