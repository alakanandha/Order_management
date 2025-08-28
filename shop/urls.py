from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views 

app_name = "shop"

urlpatterns = [
    path('', views.index, name='index'),   
    path('home/', views.home, name='home'), 
    path('login/', views.customer_login, name='customer_login'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.customer_register, name='customer_register'),
   path('logout/', views.customer_logout, name='customer_logout'),

    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:product_id>/<str:action>/', views.update_cart, name='update_cart'),

    path('checkout/', views.checkout_view, name='checkout_view'),
    path('checkout/confirm-order/', views.confirm_order, name='confirm_order'),
    path('order-success/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
]
