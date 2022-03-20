from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from customuser.views import LoginView, logout_view
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from .views import index_page, account_a_day, pdf

urlpatterns = []
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', index_page, name='index'),
    path('account_a_day', account_a_day, name='account_a_day'),
    path('pdf', pdf, name='pdf'),
    path('product/', include('tax.url')),
    path('product/', include('product.url')),
    path('', include('vendor.urls')),
    path('', include('purchase.urls')),
    path('invoice/', include('invoice.url')),
    path('transfer/', include('product_transfer.urls')),
    path('organizations/', include('organization.urls')),
    path('customer/', include('customer.urls')),
    path('user/', include('customuser.urls')),
    path('additional/', include('additional.urls')),
    path('report/', include('report.urls')),
    path('stock/', include('fromstock.urls')),
    path('return/', include('returnproduct.urls')),
    path('banks/', include('bank.urls')),
    path('cities/', include('city.urls')),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', logout_view, name='logout'),

)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
