from django.urls import path
from .views import admin_login_view,admin_dashboard,manage_products,add_product,edit_product,delete_product,manage_orders,view_order,manage_customers,logout_view

app_name = 'accounts'
urlpatterns = [
    path("admin-login/", admin_login_view, name="admin_login"),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path('logout/', logout_view, name='logout'),

    path("admin/products/", manage_products, name="manage_products"),
    path("add-product/", add_product, name="add_product"),
    path('admin/edit-product/<int:product_id>/', edit_product, name='edit_product'),
    path('admin/delete-product/<int:product_id>/', delete_product, name='delete_product'),

    path('orders/', manage_orders, name='manage_orders'),
    path('orders/<int:order_id>/', view_order, name='view_order'),

    path('customers/', manage_customers, name='manage_customers'),
]