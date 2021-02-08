from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import *
from .forms import *

# Create your views here.
def index(request):
    return render(request, 'index.html')

def register(request):
    return HttpResponse("Hello from register page")

def products(request):
    products = Product.objects.all()
    return render(request, 'products.html', { 'products': products })

def single_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'single_product.html', { 'product': product })

def product_form(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            new_product = form.save()
            return render(request, 'single_product.html', { 'product': new_product })
    else:
        form = ProductForm()
        return render(request, 'product_form.html', { 'form': form })
