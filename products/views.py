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
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    
    # Filtering logic
    q = request.GET.get('q', '').strip()
    category_slug_or_name = request.GET.get('category', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if category_slug_or_name:
        products = products.filter(Q(category__name__iexact=category_slug_or_name) | Q(category__slug__iexact=category_slug_or_name))
    
    if min_price and min_price.isdigit():
        products = products.filter(price__gte=int(min_price))
    if max_price and max_price.isdigit():
        products = products.filter(price__lte=int(max_price))
        
    context = {
        'db_products': products,
        'categories': categories,
        'search_query': q,
        'current_category': category_slug_or_name,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})
