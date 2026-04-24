from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile
from orders.models import Cart
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile') and request.user.profile.is_seller:
            return redirect('seller_dashboard')
        return redirect('home')
        
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            if hasattr(user, 'profile') and user.profile.is_seller:
                return redirect('seller_dashboard')
            return redirect('home')
        else:
            messages.error(request, "Username atau Password salah.")
    return render(request, 'login.html')

def register_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile') and request.user.profile.is_seller:
            return redirect('seller_dashboard')
        return redirect('home')
        
    if request.method == 'POST':
        u = request.POST.get('username')
        e = request.POST.get('email')
        p = request.POST.get('password')
        
        if User.objects.filter(username=u).exists():
            messages.error(request, "Username sudah terdaftar.")
        else:
            user = User.objects.create_user(username=u, email=e, password=p)
            UserProfile.objects.create(user=user, is_seller=False)
            Cart.objects.create(user=user)
            
            login(request, user)
            return redirect('home')
            
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('home')

from django.db.models import Q, Sum, F
from products.models import Product, Category
from orders.models import OrderItem, Order
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Message
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def seller_dashboard(request):
    if not getattr(request.user.profile, 'is_seller', False):
        return redirect('home')
        
    # Seed default categories
    default_cats = ['Sneakers Pria', 'Sneakers Wanita', 'Loafers', 'Kaos Kaki', 'Perawatan', 'Aksesoris']
    for c in default_cats:
        Category.objects.get_or_create(name=c, defaults={'slug': c.lower().replace(' ', '-')})
        
    categories = Category.objects.all()
        
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_product':
            cat_id = request.POST.get('category')
            cat = Category.objects.filter(id=cat_id).first()
            Product.objects.create(
                seller=request.user,
                category=cat,
                name=request.POST.get('name'),
                price=request.POST.get('price', 0),
                stock=request.POST.get('stock', 0),
                sizes=request.POST.get('sizes', ''),
                colors=request.POST.get('colors', ''),
                description=request.POST.get('description', ''),
                image=request.FILES.get('image')
            )
            return redirect('seller_dashboard')
        elif action == 'edit_product':
            product_id = request.POST.get('product_id')
            product = Product.objects.filter(id=product_id, seller=request.user).first()
            if product:
                cat_id = request.POST.get('category')
                product.category = Category.objects.filter(id=cat_id).first()
                product.name = request.POST.get('name')
                product.price = request.POST.get('price', 0)
                product.stock = request.POST.get('stock', 0)
                product.sizes = request.POST.get('sizes', '')
                product.colors = request.POST.get('colors', '')
                product.description = request.POST.get('description', '')
                image = request.FILES.get('image')
                if image:
                    product.image = image
                product.save()
                messages.success(request, 'Produk berhasil diupdate!')
            return redirect('seller_dashboard')
        elif action == 'delete_product':
            product_id = request.POST.get('product_id')
            Product.objects.filter(id=product_id, seller=request.user).delete()
            messages.success(request, 'Produk berhasil dihapus!')
            return redirect('seller_dashboard')
        elif action == 'add_category':
            cat_name = request.POST.get('name')
            if cat_name:
                from django.utils.text import slugify
                Category.objects.get_or_create(name=cat_name, defaults={'slug': slugify(cat_name)})
                messages.success(request, f'Kategori {cat_name} berhasil ditambahkan!')
            return redirect('seller_dashboard')
        elif action == 'delete_category':
            cat_id = request.POST.get('category_id')
            Category.objects.filter(id=cat_id).delete()
            messages.success(request, 'Kategori berhasil dihapus!')
            return redirect('seller_dashboard')
        elif action == 'change_password':
            p = request.POST.get('new_password')
            if p:
                request.user.set_password(p)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password berhasil diubah!')
            return redirect('seller_dashboard')
        elif action == 'update_order_status':
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('status')
            if OrderItem.objects.filter(order_id=order_id, product__seller=request.user).exists():
                order = Order.objects.filter(id=order_id).first()
                if order:
                    order.status = new_status
                    order.save()
                    messages.success(request, f'Status pesanan #{order.id} berhasil diperbarui menjadi {new_status}.')
            return redirect('seller_dashboard')
        
    my_products = Product.objects.filter(seller=request.user).order_by('-created_at')
    
    total_products = my_products.count()
    revenue = OrderItem.objects.filter(product__seller=request.user, order__status__in=['paid', 'completed', 'shipped']).aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
    new_orders_count = OrderItem.objects.filter(product__seller=request.user).values('order').distinct().count()
    
    recent_order_items = OrderItem.objects.filter(product__seller=request.user).select_related('order', 'order__user').order_by('-order__created_at')

    return render(request, 'seller_dashboard.html', {
        'my_products': my_products,
        'total_products': total_products,
        'revenue': revenue,
        'new_orders': new_orders_count,
        'recent_order_items': recent_order_items,
        'categories': categories
    })

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        profile = getattr(user, 'profile', None)
        if profile:
            profile.phone = request.POST.get('phone', '')
            profile.address = request.POST.get('address', '')
            profile.store_name = request.POST.get('store_name', '')
            profile.save()
        messages.success(request, 'Profil berhasil diperbarui!')
        return redirect('profile')
    return render(request, 'profile.html')

@login_required
def chat_seller(request, receiver_id=None):
    if request.method == 'POST':
        try:
            r_id = request.POST.get('receiver_id')
            if r_id:
                receiver = User.objects.get(id=r_id)
                Message.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    content=request.POST.get('content')
                )
                return redirect('chat_seller', receiver_id=receiver.id)
        except User.DoesNotExist:
            pass
            
    sent_msgs = Message.objects.filter(sender=request.user).values_list('receiver_id', flat=True)
    received_msgs = Message.objects.filter(receiver=request.user).values_list('sender_id', flat=True)
    user_ids = set(sent_msgs).union(set(received_msgs))
    chat_users = User.objects.filter(id__in=user_ids)
            
    messages = []
    receiver_user = None
    if receiver_id:
        receiver_user = User.objects.filter(id=receiver_id).first()
        messages = Message.objects.filter(
            Q(sender=request.user, receiver_id=receiver_id) | 
            Q(sender_id=receiver_id, receiver=request.user)
        ).order_by('timestamp')
        
    return render(request, 'chat_seller.html', {'chat_messages': messages, 'receiver': receiver_user, 'chat_users': chat_users})

