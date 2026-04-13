from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
from django.db.models import Sum, F

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    qty = int(request.POST.get('quantity', 1))
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += qty
    else:
        cart_item.quantity = qty
    cart_item.save()
    return redirect('cart')

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        action = request.POST.get('action')
        if action == 'increase':
            if item.quantity < item.product.stock:
                item.quantity += 1
                item.save()
        elif action == 'decrease':
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()
        elif action == 'remove':
            item.delete()
    return redirect('cart')

@login_required
def cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product')
    total = sum(item.product.price * item.quantity for item in items)
    return render(request, 'cart.html', {'cart_items': items, 'total': total})

@login_required
def checkout(request):
    cart = getattr(request.user, 'cart', None)
    if not cart or not cart.items.exists():
        return redirect('home')
        
    items = cart.items.all()
    total = sum(item.product.price * item.quantity for item in items)
    
    if request.method == 'POST':
        try:
            shipping_cost = int(request.POST.get('shipping_cost', 0))
        except ValueError:
            shipping_cost = 0
            
        order = Order.objects.create(
            user=request.user,
            total_price=total + shipping_cost,
            shipping_address=request.POST.get('address', 'Alamat Dummy')
        )
        for item in items:
            OrderItem.objects.create(
                order=order, product=item.product, quantity=item.quantity, price=item.product.price
            )
        items.delete() # Clear cart
        return redirect('payment', order_id=order.id)
        
    return render(request, 'checkout.html', {'cart_items': items, 'total': total})

@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == 'POST':
        payment_method = request.POST.get('payment', 'bank_transfer')
        order.payment_method = payment_method
        
        if payment_method == 'bank_transfer':
            if 'payment_proof' in request.FILES:
                order.payment_proof = request.FILES['payment_proof']
                order.status = 'paid'
            else:
                # Optional: Handle missing file gracefully, though HTML5 handles it
                order.status = 'pending'
        else:
            order.status = 'paid'
            
        order.save()
        return redirect('order_detail', order_id=order.id)
        
    return render(request, 'payment.html', {'order': order})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    is_buyer = order.user == request.user
    is_seller = order.items.filter(product__seller=request.user).exists()
    
    if not (is_buyer or is_seller):
        return redirect('home')
        
    if request.method == 'POST' and is_seller:
        old_status = order.status
        order.status = request.POST.get('status', order.status)
        resi = request.POST.get('tracking_number')
        if resi is not None:
            order.tracking_number = resi.strip()
            
        if old_status != 'completed' and order.status == 'completed':
            for item in order.items.all():
                if item.product.stock >= item.quantity:
                    item.product.stock -= item.quantity
                else:
                    item.product.stock = 0
                item.product.save()
                
        order.save()
        return redirect('order_detail', order_id=order.id)
        
    return render(request, 'order_detail.html', {'order': order, 'is_seller_view': is_seller})

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_list.html', {'orders': orders})
