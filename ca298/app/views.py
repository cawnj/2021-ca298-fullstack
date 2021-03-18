from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import *
from django.views.generic import CreateView
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .permissions import admin_required

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


def register(request):
    return HttpResponse("Hello from register page")


def products(request):
    all_products = Product.objects.all()
    return render(request, 'products.html', { 'products': all_products })


def single_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'single_product.html', { 'product': product })


@login_required
@admin_required
def product_form(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
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
    # TODO: handle product id gracefully
    shopping_basket = ShoppingBasket.objects.filter(user_id=user.id).first()
    product = Product.objects.get(pk=product_id)
    sbi = ShoppingBasketItems.objects.filter(basket_id=shopping_basket.id, product_id=product.id).first()
    if not sbi:
        sbi = ShoppingBasketItems(basket_id=shopping_basket.id, product_id=product.id).save()
    else:
        sbi.quantity += 1
        sbi.save()
    return render(request, 'single_product.html', { 'product': product, 'added': True })


@login_required
def view_basket(request):
    shopping_basket = ShoppingBasket.objects.filter(user_id=request.user.id).first()
    shopping_basket_items = ShoppingBasketItems.objects.filter(basket_id=shopping_basket.id)
    sb_products = {}
    for item in shopping_basket_items:
        product = Product.objects.filter(id=item.product_id).first()
        sb_products[product] = item.quantity
    return render(request, 'shopping_basket.html', { 'sb_products': sb_products })


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
        form = OrderForm()
        return render(request, 'checkout.html', { 'form': form })


@login_required
def order_complete(request, order_id):
    order_items = OrderItems.objects.filter(order_id=order_id)
    order_products = {}
    for item in order_items:
        product = Product.objects.filter(id=item.product_id).first()
        order_products[product] = item.quantity
    return render(request, 'order_complete.html', { 'order_products': order_products })
