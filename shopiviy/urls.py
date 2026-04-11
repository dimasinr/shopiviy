"""shopiviy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from products.views import home, product_detail, product_list
from orders.views import cart, checkout, payment, order_detail, add_to_cart, order_list, update_cart_item
from accounts.views import seller_dashboard, chat_seller, login_view, register_view, logout_view, profile_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    
    # Products / Home
    path('', home, name='home'),
    path('products/', product_list, name='product_list'),
    path('product-detail/<int:product_id>/', product_detail, name='product_detail'),
    
    # Orders
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', update_cart_item, name='update_cart_item'),
    path('cart/', cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('payment/<int:order_id>/', payment, name='payment'),
    path('order/detail/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/', order_list, name='order_list'),
    
    # Accounts / Seller
    path('seller/dashboard/', seller_dashboard, name='seller_dashboard'),
    path('seller/chat/', chat_seller, name='chat_seller'),
    path('seller/chat/<int:receiver_id>/', chat_seller, name='chat_seller'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
