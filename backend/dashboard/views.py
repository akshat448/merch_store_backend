from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, StreamingHttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Sum

from order.models import Order, OrderItem, Payment
from products.models import Product, CartItem
from login.models import CustomUser
from discounts.models import DiscountCode
from .forms import DiscountCodeForm

import csv
import qrcode
from io import BytesIO
from datetime import datetime

class ListItem:
    def __init__(self, id, name, price, orders_count):
        self.id = id
        self.name = name
        self.price = price
        self.orders_count = orders_count


# Create your views here.

@staff_member_required
def dashboard(request):
    amount_received = Order.objects.filter(is_verified=True).aggregate(total=Sum('amount'))['total'] or 0
    unsuccessful_orders = Order.objects.filter(is_verified=False).count()
    pending_orders = Order.objects.filter(is_verified=None).count()
    items_ordered = OrderItem.objects.all().aggregate(total=Sum('quantity'))['total'] or 0

    items = []
    products = Product.objects.all()
    for product in products:
        orders_count = OrderItem.objects.filter(product=product, order__is_verified=True).count()
        item = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'orders_count': orders_count
        }
        items.append(item)

    users = CustomUser.objects.all()
    user_orders = {user: Order.objects.filter(user=user) for user in users}
    payments = Payment.objects.all()

    context = {
        'amount_received': amount_received,
        'items_ordered': items_ordered,
        'unsuccessful_orders': unsuccessful_orders,
        'pending_orders': pending_orders,
        'items': items,
        'productsCount': len(items),
        'user_orders': user_orders,
        'payments': payments
    }

    return render(request, 'dashboard/dashboard.html', context=context)


@staff_member_required
def import_users_from_login(request):
    login_users = CustomUser.objects.all()
    User = get_user_model()
    imported_users_count = 0
    for login_user in login_users:
        user, created = User.objects.get_or_create(email=login_user.email, defaults={'Phone_Num': login_user.Phone_Num, 'name': login_user.name})
        if created:
            imported_users_count += 1
    messages.success(request, f"{imported_users_count} users imported from LOGIN app successfully.")
    return redirect('admin_dashboard')


@staff_member_required
def list_discount_codes(request):
    discount_codes = DiscountCode.objects.all()
    return render(request, 'dashboard/list_discount_codes.html', {'discount_codes': discount_codes})

@staff_member_required
def create_discount_code(request):
    if request.method == 'POST':
        form = DiscountCodeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Discount code created successfully.')
            return redirect('list_discount_codes')
    else:
        form = DiscountCodeForm()
    return render(request, 'dashboard/discount_code_form.html', {'form': form})

@staff_member_required
def edit_discount_code(request, code_id):
    discount_code = get_object_or_404(DiscountCode, id=code_id)
    if request.method == 'POST':
        form = DiscountCodeForm(request.POST, instance=discount_code)
        if form.is_valid():
            form.save()
            messages.success(request, 'Discount code updated successfully.')
            return redirect('list_discount_codes')
    else:
        form = DiscountCodeForm(instance=discount_code)
    return render(request, 'dashboard/discount_code_form.html', {'form': form})


class Echo:
    def write(self, value):
        return value

@staff_member_required
def ordersCSV(request, id):
    if request.method=='GET':
        raise Http404
    product = Product.objects.filter(id=id).first()
    if product is None:
        raise Http404
    order_items = OrderItem.objects.filter(product=product, order__is_verified=True).all()
    rows = []
    first_row = ['Name', 'email id', 'Phone Number', 'position']
    if product.is_size_required:
        first_row.append('Size')
    if product.is_name_required:
        first_row.append('Printing Name')
    if product.is_image_required:
        first_row.append('Image URL')
    rows.append(first_row)
    for item in order_items:
        user = item.order.user
        row = [user.name, user.email, user.Phone_Num, user.position]
        if product.is_size_required:
            row.append(item.size)
        if product.is_name_required:
            row.append(item.printing_name)
        if product.is_image_required:
            row.append(item.image_url)
        rows.append(row)
    psudo_buffers = Echo()
    writer = csv.writer(psudo_buffers)
    return StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type='text/csv',
        headers = {'Content-Disposition': f'attachment; filename="{product.name}_orders.csv"'}
    )


@staff_member_required
@require_POST
def stopOrders(request):
    products = Product.objects.all()
    for product in products:
        product.accept_orders = False
        product.save()
    cart_items = CartItem.objects.all()
    for cart_item in cart_items:
        cart_item.delete()
    messages.success(request, 'Stopped receiving orders and cleared all carts')
    return redirect('/dashboard')

"""
@staff_member_required
def scan_qr(request):
    if request.method == 'POST':
        scanned_qr_code = request.POST.get('scanned_qr_code')
        try:
            order_id = int(scanned_qr_code)
            order = Order.objects.get(pk=order_id)
            # Mark the order as delivered
            order.delivered = True
            order.save()
            return redirect('admin_dashboard')  # Redirect to admin dashboard after marking order as delivered
        except Order.DoesNotExist:
            return HttpResponseNotFound("Order not found")
        except ValueError:
            return HttpResponseNotFound("Invalid QR code")
    return render(request, 'scan_qr.html')
"""