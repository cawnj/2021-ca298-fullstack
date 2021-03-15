from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, CaUser
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
        form = ProductForm(request.POST)
        if form.is_valid():
            new_product = form.save()
            return render(request, 'single_product.html', { 'product': new_product })
    else:
        form = ProductForm()
        return render(request, 'product_form.html', { 'form': form })
