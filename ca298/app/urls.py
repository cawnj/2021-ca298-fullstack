from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/',views.register, name='register'),
    path('products/', views.products, name="products"),
    path('product/<int:product_id>', views.single_product, name="single_product"),
    path('productform', views.product_form, name="product_form"),
]