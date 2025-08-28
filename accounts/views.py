from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login
from django.contrib import messages
from .forms import AdminLoginForm
from .models import Product
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from shop.models import Order
from django.contrib.auth import get_user_model

def admin_login_view(request):
    if request.method == "POST":
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:  
                login(request, user)
                return redirect("accounts:admin_dashboard")  
            else:
                messages.error(request, "Invalid credentials")
    else:
        form = AdminLoginForm()
    return render(request, "accounts/admin_login.html", {"form": form})


def is_admin(user):
    return user.is_superuser  


@login_required
@user_passes_test(is_admin)  
def admin_dashboard(request):
    return render(request, "accounts/admin_dashboard.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('accounts:admin_login') 


def manage_products(request):
    query = request.GET.get('q')  
    if query:
        products = Product.objects.filter(name__icontains=query) 
    else:
        products = Product.objects.all()
    return render(request, 'accounts/manage_products.html', {'products': products})


def add_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        brand = request.POST.get("brand")
        description = request.POST.get("description")
        original_price = request.POST.get("original_price")
        selling_price = request.POST.get("selling_price")
        quantity = request.POST.get("quantity")
        delivery_fee=request.POST.get("delivery_fee")
        photo = request.FILES.get("photo")
      
        
        
        Product.objects.create(
            name=name,
            brand=brand,
           
            description=description,
            original_price=original_price,
            selling_price=selling_price,
            quantity=quantity,
            delivery_fee=delivery_fee,
            photo=photo
        )
        return redirect("accounts:manage_products") 
    

    return render(request, "accounts/add_products.html")



def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.brand = request.POST.get("brand")
        product.description = request.POST.get("description")
        product.original_price = request.POST.get("original_price")
        product.selling_price = request.POST.get("selling_price")
        product.delivery_fee=request.POST.get("delivery_fee")
        product.quantity = request.POST.get("quantity")

        if request.FILES.get("photo"):
            product.photo = request.FILES.get("photo")

        product.save()
        return redirect("accounts:manage_products")

    return render(request, "accounts/edit_product.html", {"product": product})



def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.delete()
        return redirect("accounts:manage_products")

    return render(request, "accounts/delete_product.html", {"product": product})



def manage_orders(request):
    status_filter = request.GET.get('status')
    orders = Order.objects.all().order_by('-id')
    if status_filter:
        orders = orders.filter(status=status_filter)

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        status = request.POST.get("status")
        tracking_id = request.POST.get("tracking_id")

        try:
            order = Order.objects.get(id=order_id)
            order.status = status
            order.tracking_id = tracking_id
            order.save()
            messages.success(request, f"Order #{order.id} updated successfully.")
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")

        
        redirect_url = request.path
        if status_filter:
            redirect_url += f"?status={status_filter}"
        return redirect(redirect_url)

    return render(request, 'accounts/manage_orders.html', {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter
    })


def view_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    status_choices = Order.STATUS_CHOICES

    if request.method == "POST":
        status = request.POST.get('status')
        tracking_id = request.POST.get('tracking_id')
        order.status = status
        order.tracking_id = tracking_id
        order.save()
        return redirect('accounts:view_order', order_id=order.id)

    return render(request, 'accounts/view_order.html', {
        'order': order,
        'status_choices': status_choices
    })

 



User = get_user_model()

def manage_customers(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            if not user.is_superuser:  
                user.delete()
                messages.success(request, f"{user.username} has been removed.")
            else:
                messages.error(request, "Cannot remove admin user.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

        return redirect("accounts:manage_customers")

    customers = User.objects.filter(is_superuser=False)

    return render(request, "accounts/manage_customers.html", {
        "customers": customers
    })
