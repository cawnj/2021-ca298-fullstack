from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import *
from django.views.generic import CreateView
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .permissions import admin_required
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from rest_framework import viewsets
from .serializers import *


# Create your views here.


class CaUserSignupView(CreateView):
    model = CaUser
    form_class = CaSignupForm
    template_name = 'user_signup.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/')


class AdminSignupView(CreateView):
    model = CaUser
    form_class = AdminSignupForm
    template_name = 'admin_signup.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/')


class Login(LoginView):
    template_name = 'login.html'


def logout_view(request):
    logout(request)
    return redirect('/')


def index(request):
    return render(request, 'index.html')


def products(request):
    all_products = Product.objects.all()
    flag = request.GET.get('format', '')
    if flag == "json":
        serialized_products = serializers.serialize("json", all_products)
        return HttpResponse(serialized_products, content_type="application/json")
    else:
        return render(request, 'products.html', { 'products': all_products })


def single_product(request, product_id):
    does_not_exist = False
    product = Product.objects.filter(pk=product_id).first()
    if not product:
        does_not_exist = True
    return render(request, 'single_product.html', { 'product': product, 'does_not_exist': does_not_exist })


@login_required
@admin_required
def product_form(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponse("invalid form!")
        new_product = form.save()
        return redirect('/product/' + str(new_product.id))

    else:
        form = ProductForm()
        return render(request, 'product_form.html', { 'form': form })


@login_required
def add_to_basket(request, product_id):
    user = request.user
    shopping_basket = ShoppingBasket.objects.filter(user_id=user.id).first()
    if not shopping_basket:
        shopping_basket = ShoppingBasket(user_id=user.id).save()
    shopping_basket = ShoppingBasket.objects.filter(user_id=user.id).first()
    try:
        product = Product.objects.get(pk=product_id)
    except ObjectDoesNotExist:
        return render(request, 'single_product.html', { 'does_not_exist': True })
    sbi = ShoppingBasketItems.objects.filter(basket_id=shopping_basket.id, product_id=product.id).first()
    if not sbi:
        sbi = ShoppingBasketItems(basket_id=shopping_basket.id, product_id=product.id).save()
    else:
        sbi.quantity += 1
        sbi.save()
    return render(request, 'single_product.html', { 'product': product, 'added': True })


@login_required
def view_basket(request):
    is_empty = False
    sb_products = {}
    shopping_basket = ShoppingBasket.objects.filter(user_id=request.user.id).first()
    if shopping_basket:
        shopping_basket_items = ShoppingBasketItems.objects.filter(basket_id=shopping_basket.id)
        for item in shopping_basket_items:
            product = Product.objects.filter(id=item.product_id).first()
            sb_products[product] = item.quantity
    if not shopping_basket or len(sb_products) == 0:
        is_empty = True
    return render(request, 'shopping_basket.html', { 'sb_products': sb_products, 'empty': is_empty })


@login_required
def checkout(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if not form.is_valid():
            return HttpResponse("invalid form!")
        order = form.save(commit=False)
        order.user_id = request.user.id
        order.save()

        shopping_basket = ShoppingBasket.objects.filter(user_id=request.user.id).first()
        shopping_basket_items = ShoppingBasketItems.objects.filter(basket_id=shopping_basket.id)
        for item in shopping_basket_items:
            order_item = OrderItems(order_id=order.id, product_id=item.product_id, quantity=item.quantity)
            order_item.save()
        shopping_basket.delete()
        return redirect('/order_complete/' + str(order.id))
    else:
        empty = False
        shopping_basket = ShoppingBasket.objects.filter(user_id=request.user.id).first()
        if not shopping_basket:
            empty = True
        form = OrderForm()
        return render(request, 'checkout.html', { 'form': form, 'empty': empty })


@login_required
def order_complete(request, order_id):
    does_not_exist = False
    order_products = {}
    order_items = OrderItems.objects.filter(order_id=order_id)
    if len(order_items) == 0:
        does_not_exist = True
    for item in order_items:
        product = Product.objects.filter(id=item.product_id).first()
        order_products[product] = item.quantity
    return render(request, 'order_complete.html', { 'order_products': order_products, 'does_not_exist': does_not_exist })


class UserViewSet(viewsets.ModelViewSet):
    queryset = CaUser.objects.all()
    serializer_class = UserSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
