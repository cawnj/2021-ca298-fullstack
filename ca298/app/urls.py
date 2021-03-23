from django.urls import path
from . import views
from .forms import *

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.products, name="products"),
    path('product/<int:product_id>', views.single_product, name="single_product"),
    path('productform/', views.product_form, name="product_form"),
    path('register/', views.CaUserSignupView.as_view(), name="register"),
    path('adminsignup/', views.AdminSignupView.as_view(), name="admin_signup"),
    path('login/', views.Login.as_view(template_name="login.html", authentication_form=UserLoginForm), name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('addbasket/<int:product_id>', views.add_to_basket, name="add_to_basket"),
    path('basket/', views.view_basket, name="view_basket"),
    path('checkout/', views.checkout, name="checkout"),
    path('order_complete/<int:order_id>', views.order_complete, name="order_complete"),
]
