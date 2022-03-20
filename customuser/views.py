from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views import View
from customuser.models import CustomUser
from organization.models import Organization
from django.contrib import messages
from invoice.models import Invoice
from product_transfer.models import ProductTransfer
from purchase.models import Purchase
from fromstock.models import ProductInStock
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


class CustomUserView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = ''

    def get(self, request, *args, **kwargs):
        current_org = get_object_or_404(CustomUser, username=request.user.username).organization
        customers = CustomUser.objects.filter(organization=current_org)
        if request.user.is_superuser:
            customers = CustomUser.objects.all()
        context = {
            'current_org': current_org,
            'customusers': customers
        }
        if request.user.is_superuser:
            context['organizations'] = Organization.objects.all()
        return render(request, 'customuser/customusers.html', context=context)

    def post(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            current_org = get_object_or_404(CustomUser, username=request.user.username).organization
            required = ['password', 'username', 'organization']
            for r in required:
                if r not in request.POST:
                    messages.error(request, f'{r} is required')
                    return redirect(reverse('customusers'))
            email = request.POST['email'] if 'email' in request.POST else None
            staff = request.POST['email'] if 'email' in request.POST else None
            try:
                u = CustomUser(
                    username=request.POST['username'],
                    email=email,
                    organization_id=request.POST['organization'] if request.user.is_superuser else current_org.id,
                    is_staff=True if staff else False
                )
                u.set_password(request.POST['password'])
                u.save()
            except:
                messages.error(request, 'Username already exists')
        return redirect(reverse('customusers'))


@login_required(login_url='/login/')
def single_customuser(request, id, *args, **kwargs):
    object = get_object_or_404(CustomUser, id=id)
    invoices = Invoice.objects.filter(user=object)
    transfered = ProductTransfer.objects.filter(user=object)
    bought = Purchase.objects.filter(user=object)
    stock = ProductInStock.objects.filter(user=object)
    sold_product = Invoice.objects.filter(user=object,)



    context = {
        'object': object,
        'invoices': invoices,
        'transfered': transfered,
        'bought': bought,
        'stock': stock,
        's_product':sold_product
    }

    return render(request, 'customuser/single_customuser.html', context=context)


class LoginView(View):
    def get(self, request):
        context = {}
        return render(request, 'customuser/login.html', context)

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is None:
            context = {
                ''
            }
            messages.error(request, 'username or password invalid')
            return render(request, "customuser/login.html")
        login(request, user)
        return redirect("index")


def logout_view(request):
    logout(request)
    return redirect('login')
