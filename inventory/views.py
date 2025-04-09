"""Admin configuration for the inventory app."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Report
from .forms import RegisterForm, ProductForm, OrderForm
from datetime import date
from django.db.models import F, Sum
from django.http import HttpResponseForbidden
from django.contrib import messages
# Home Dashboard (optional)
def dashboard(request):
    return render(request, 'inventory/dashboard.html')

# Register
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'inventory/register.html', {'form': form})

# ✅ Fixed Login with Role-Based Redirect
def login_view(request):
    if request.method == 'POST':
        uname = request.POST['username']
        pwd = request.POST['password']
        user = authenticate(request, username=uname, password=pwd)
        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('product_list')
            else:
                return redirect('user_dashboard')
    return render(request, 'inventory/login.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# ✅ Regular User Dashboard - View Products and Create Orders
@login_required
def user_dashboard(request):
    if request.user.is_superuser:
        return redirect('product_list')

    products = Product.objects.all()

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            return redirect('user_dashboard')
    else:
        form = OrderForm()

    return render(request, 'inventory/user_dashboard.html', {
        'products': products,
        'form': form,
    })

# ✅ Admin-only Product List
@login_required
def product_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to view this page.")
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

# Admin-only Create Product
@login_required
def product_create(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to perform this action.")
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'inventory/product_form.html', {'form': form})

# Admin-only Update Product
@login_required
def product_update(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to perform this action.")
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'inventory/product_form.html', {'form': form})

# Admin-only Delete Product
@login_required
def product_delete(request, pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to perform this action.")
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('product_list')



def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            product = order.product
            quantity_requested = order.quantity

            if product.quantity == 0:
                messages.error(request, f"'{product.name}' is out of stock.")
            elif quantity_requested > product.quantity:
                messages.error(request, f"Only {product.quantity} units of '{product.name}' are available.")
            else:
                # Reduce product stock
                product.quantity -= quantity_requested
                product.save()
                order.save()
                messages.success(request, "Order placed successfully.")
                return redirect('user_dashboard')
    else:
        form = OrderForm()

    return render(request, 'inventory/order_form.html', {'form': form})


# Stock Alerts for Admin
@login_required
def stock_alerts(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to view this page.")
    alerts = Product.objects.filter(quantity__lte=F('low_stock_threshold'))
    return render(request, 'inventory/alert_list.html', {'alerts': alerts})

# Reports for Admin
@login_required
def generate_report(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to view this page.")
    today = date.today()
    total_orders = Order.objects.filter(order_date__date=today).count()
    total_sales = Order.objects.filter(order_date__date=today).aggregate(
        total=Sum(F('quantity') * F('product__price'))
    )['total'] or 0
    Report.objects.create(report_date=today, total_orders=total_orders, total_sales=total_sales)
    return render(request, 'inventory/report.html', {
        'date': today,
        'orders': total_orders,
        'sales': total_sales
    })
