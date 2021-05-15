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
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt


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
    product = Product.objects.filter(pk=product_id).first()
    return render(request, 'single_product.html', { 'product': product })


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


@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def add_to_basket(request, product_id):
    flag = request.GET.get('format', '')
    user = request.user
    if user.is_anonymous:
        token = request.META.get('HTTP_AUTHORIZATION').split(" ")[1]
        user = Token.objects.get(key=token).user
    shopping_basket = ShoppingBasket.objects.filter(user_id=user.id).first()
    if not shopping_basket:
        shopping_basket = ShoppingBasket(user_id=user.id).save()
        shopping_basket = ShoppingBasket.objects.filter(user_id=user.id).first()
    try:
        product = Product.objects.get(pk=product_id)
    except ObjectDoesNotExist:
        if flag == "json":
            return JsonResponse({'status': 'failed', 'reason': 'does-not-exist'})
        else:
            return render(request, 'single_product.html', {'product': None})
    sbi = ShoppingBasketItems.objects.filter(basket_id=shopping_basket.id, product_id=product.id).first()
    if not sbi:
        sbi = ShoppingBasketItems(basket_id=shopping_basket.id, product_id=product.id).save()
    else:
        sbi.quantity += 1
        sbi.save()
    if flag == "json":
        return JsonResponse({'status': 'success', 'product-id': product_id})
    else:
        return render(request, 'single_product.html', { 'product': product, 'added': True })


@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def view_basket(request):
    user = request.user
    if user.is_anonymous:
        token = request.META.get('HTTP_AUTHORIZATION').split(" ")[1]
        user = Token.objects.get(key=token).user
    shopping_basket = ShoppingBasket.objects.filter(user_id=user.id).first()
    if not shopping_basket:
        shopping_basket = ShoppingBasket(user_id=user.id).save()
        shopping_basket = ShoppingBasket.objects.filter(user_id=user.id).first()
    sbi = ShoppingBasketItems.objects.filter(basket_id=shopping_basket.id)
    flag = request.GET.get('format', '')
    if flag == "json":
        basket_array = []
        for item in sbi:
            basket_array.append({
                'product': item.product.name,
                'price': float(item.product.price),
                'quantity': int(item.quantity)
            })
        return HttpResponse(json.dumps({'items': basket_array}), content_type="application/json")
    return render(request, 'shopping_basket.html', { 'basket': shopping_basket, 'items': sbi })


@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
@csrf_exempt
def checkout(request):
    flag = request.GET.get('format', '')
    user = request.user
    if user.is_anonymous:
        token = request.META.get('HTTP_AUTHORIZATION').split(" ")[1]
        user = Token.objects.get(key=token).user
    shopping_basket = ShoppingBasket.objects.filter(user_id=user.id).first()
    if not shopping_basket:
        shopping_basket = ShoppingBasket(user_id=user.id).save()
        shopping_basket = ShoppingBasket.objects.filter(user_id=user.id).first()
    sbi = ShoppingBasketItems.objects.filter(basket_id=shopping_basket.id)
    if not sbi:
        if flag == "json":
            return JsonResponse({'status': 'failed', 'reason': 'empty-basket'})
        else:
            return render(request, 'checkout.html', {'items': None})

    if request.method == 'POST':
        if not request.POST:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            form = OrderForm(body)
        else:
            form = OrderForm(request.POST)

        if not form.is_valid():
            if flag == "json":
                return JsonResponse({'status': 'failed', 'reason': 'invalid-form', 'errors': form.errors})
            else:
                return HttpResponse("invalid form!")
        order = form.save(commit=False)
        order.user_id = user.id
        order.save()
        shopping_basket = ShoppingBasket.objects.filter(user_id=user.id).first()
        shopping_basket_items = ShoppingBasketItems.objects.filter(basket_id=shopping_basket.id)
        for item in shopping_basket_items:
            order_item = OrderItems(order_id=order.id, product_id=item.product_id, quantity=item.quantity)
            order_item.save()
        shopping_basket.delete()
        if flag == "json":
            return JsonResponse({'status': 'success', 'order-id': order.id})
        else:
            return redirect('/order_complete/' + str(order.id))
    else:
        form = OrderForm()
        return render(request, 'checkout.html', { 'form': form, 'items': sbi })


@login_required
def order_complete(request, order_id):
    order_items = OrderItems.objects.filter(order_id=order_id)
    return render(request, 'order_complete.html', { 'items': order_items })


class UserViewSet(viewsets.ModelViewSet):
    queryset = CaUser.objects.all()
    serializer_class = UserSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = []
    permission_classes = []
