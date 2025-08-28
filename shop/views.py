
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CustomerRegisterForm, CustomerLoginForm
from .models import CustomerProfile, Address, Order
from django.contrib.auth import get_user_model
from accounts.models import Product
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'shop/index.html') 


import re

User = get_user_model()

def customer_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        state = request.POST.get("state")
        district = request.POST.get("district")
        pincode = request.POST.get("pincode")
        address = request.POST.get("address")

       
        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Phone number must be 10 digits")
            return redirect("shop:customer_register")

        if not email.endswith("@gmail.com"):
            messages.error(request, "Only Gmail accounts allowed")
            return redirect("shop:customer_register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("shop:customer_register")

        if CustomerProfile.objects.filter(phone=phone).exists():
            messages.error(request, "Phone already registered")
            return redirect("shop:customer_register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("shop:customer_register")

        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password):
            messages.error(request, "Password must be strong (8+ chars, include uppercase & number)")
            return redirect("shop:customer_register")

       
        user = User.objects.create_user(username=username, email=email, password=password)
        CustomerProfile.objects.create(
            user=user, phone=phone, state=state, district=district, pincode=pincode, address=address
        )
        messages.success(request, "Registration successful! Please login.")
        return redirect("shop:customer_login")

    return render(request, "shop/register.html")

def profile_view(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-order_date')
    address = Address.objects.filter(user=user).order_by('-id').first()  # latest address

    return render(request, 'shop/profile.html', {
        'user': user,
        'orders': orders,
        'address': address
    })


def customer_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            
            return redirect("shop:home") 
        else:
            messages.error(request, "Invalid username or password")
            return redirect("shop:customer_login")

    return render(request, "shop/login.html")


def customer_logout(request):
    logout(request)
    return redirect("shop:customer_login")


def home(request):
    products = Product.objects.all()
    return render(request, 'shop/home.html', {'products': products})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    
    if 'cart' not in request.session:
        request.session['cart'] = {}

    cart = request.session['cart']

    
    current_qty = cart.get(str(product.id), 0)

    # Total quantity cannot exceed stock
    new_qty = min(current_qty + quantity, product.quantity)

    cart[str(product.id)] = new_qty
    request.session['cart'] = cart
    return redirect('shop:cart')



def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    shipping_fee = 60  #shipping fee

    for pid, qty in cart.items():
        product = Product.objects.get(id=pid)
        subtotal = product.selling_price * qty
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': qty,
            'subtotal': subtotal
        })

    context = {
        'cart_items': cart_items,
        'total': total,
        'shipping_fee': shipping_fee,
        'grand_total': total + shipping_fee
    }
    
    return render(request, 'shop/cart.html', context)



def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('cart')


# Update quantity(increase/decrease)
def update_cart(request, product_id, action):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    product = get_object_or_404(Product, id=product_id)
    current_qty = cart.get(product_id, 0)

    if action == 'increase' and current_qty < product.quantity:
        cart[product_id] = current_qty + 1
    elif action == 'decrease' and current_qty > 1:
        cart[product_id] = current_qty - 1
    elif action == 'remove':
        cart.pop(product_id, None)

    request.session['cart'] = cart
    return redirect('shop:cart')



@login_required
def checkout_view(request):
    user = request.user
    cart = request.session.get('cart', {})

    # Fetch user's latest address if exists
    try:
        address = Address.objects.filter(user=user).latest('created_at')
    except Address.DoesNotExist:
        address = None

    if request.method == "POST":
        # Add new address or use existing
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        line1 = request.POST.get('address_line1')
        line2 = request.POST.get('address_line2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')

        address = Address.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            address_line1=line1,
            address_line2=line2,
            city=city,
            state=state,
            pincode=pincode
        )

        # Create orders for each cart item
        for pid, qty in cart.items():
            product = Product.objects.get(id=pid)
            Order.objects.create(
                user=user,
                product=product,
                quantity=qty,
                address=address,
                total_price=product.selling_price * qty
            )

        # Clear cart
        request.session['cart'] = {}
        return render(request, 'shop/order_success.html', {'address': address})

    return render(request, 'shop/checkout.html', {'cart': cart, 'address': address})


def confirm_order(request):
    user = request.user
    # Get latest address
    address = Address.objects.filter(user=user).order_by('-id').first()
    if not address:
        return redirect('shop:checkout_view')

    # Get cart from session
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('shop:cart')

    ordered_items = []

    # Create orders for each cart item
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        total_price = product.selling_price * quantity
        order = Order.objects.create(
            user=user,
            product=product,
            quantity=quantity,
            address=address,
            payment_method="Cash on Delivery",
            total_price=total_price
        )
        ordered_items.append(order)
        # Reduce stock
        product.quantity -= quantity
        product.save()

    # Clear cart after order
    request.session['cart'] = {}

    # Render order success page with details
    return render(request, 'shop/order_success.html', {
        'address': address,
        'ordered_items': ordered_items,
    })


def order_success(request):
    return render(request, 'shop/order_success.html')



@login_required
def my_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-id')  # latest orders first
    return render(request, 'shop/my_orders.html', {'orders': orders})