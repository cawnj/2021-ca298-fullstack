from django.urls import path
from . import views
from .forms import *

urlpatterns = [
    path('', views.index, name='index'),
    path('register/',views.register, name='register'),
    path('products/', views.products, name="products"),
    path('product/<int:product_id>', views.single_product, name="single_product"),
    path('productform', views.product_form, name="product_form"),
    path('usersignup/', views.CaUserSignupView.as_view(), name="user_signup"),
    path('adminsignup/', views.AdminSignupView.as_view(), name="admin_signup"),
    path('login/', views.Login.as_view(template_name="login.html", authentication_form=UserLoginForm), name="login"),
    path('logout/', views.logout_view, name="logout"),
]