from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.db.models import Q

def home(request):
    q = request.GET.get('q', '').strip()
    if q:
        products = Product.objects.filter(Q(name__icontains=q) | Q(description__icontains=q)).order_by('-created_at')
    else:
        products = Product.objects.all().order_by('-created_at')[:10]
    return render(request, 'index.html', {'db_products': products, 'search_query': q})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'db_products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})
