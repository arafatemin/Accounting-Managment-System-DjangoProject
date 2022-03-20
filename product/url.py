from django.urls import path
from .views import *



urlpatterns = [
    path('unit_types/',UnitTypeView.as_view(),name='unit_type'),
    path('product_categories/',ProductCategoryView.as_view(),name='product_category'),
    path('products/',ProductView.as_view(),name='products'),
    path('product/<int:id>/',product_detail,name='product_detail'),
    path('product_update/<int:id>/',update_product,name='update_product'),
    path('products_update/<int:id>/',update_products,name='update_products'),
    path('import/',import_product,name='import_product')
]