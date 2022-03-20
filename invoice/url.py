from django.urls import path,include
from .views import InvoiceView,AddInvoice,single_invoice,download_pdf,send_email,edit_invoice
from rest_framework.routers import DefaultRouter
from .viewsets import ProductViewSet,login_view,TaxViewSer,CustomerViewSet,BankViewSet,add_invoice,InvoiceViewSet
from .views import get_product_stock, export_excel


router = DefaultRouter()
router.register('products',ProductViewSet,basename='urls')
router.register('tax',TaxViewSer,basename='taxes')
router.register('customers',CustomerViewSet,basename='customers')
router.register('bank',BankViewSet,basename='banks')
router.register('invoice-get',InvoiceViewSet,basename='invoice_get')


urlpatterns = [
    path('',InvoiceView.as_view(),name='invoices'),
    path('add/',AddInvoice.as_view(),name='add_invoice'),
    path('<int:id>',single_invoice,name='single_invoice'),
    path('edit_invoice/<int:id>',edit_invoice,name='edit_invoice'),
    path('pdf/<int:id>',download_pdf,name='invoice_pdf'),
    path('export_excel/',export_excel,name='export_excel'),
    path('api/',include(router.urls)),
    path('api/login/',login_view,name='login_viewset'),
    path('api/invoice/',add_invoice,name='add_invoice_api'),
    path('email/<int:id>/',send_email,name='send_email'),
    path('stock/unit/<int:id>/',get_product_stock,name='product_stock')
]