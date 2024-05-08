from django.shortcuts import render, redirect
from django.http import Http404, StreamingHttpResponse, HttpResponseBadRequest, FileResponse, HttpResponse, HttpResponseNotFound
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.views.decorators.http import require_POST
from django.contrib import messages

from order.models import Order, OrderItem, Payment
from products.models import Product, CartItem
from login.models import CustomUser

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
    amount_received = 0
    all_orders = Order.objects.filter(is_verified=True).all()
    for order in all_orders:
        amount_received += int(float(order.amount))
    unsuccessful_orders = Order.objects.filter(is_verified=False).count()
    pending_orders = Order.objects.filter(is_verified=None).count()
    items_ordered = 0
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
        items_ordered += orders_count
    context = {
        'amount_received': amount_received,
        'items_ordered': items_ordered,
        'unsuccessful_orders': unsuccessful_orders,
        'pending_orders': pending_orders,
        'items': items,
        'productsCount': len(items)
    }
    return render(request, 'dashboard/dashboard.html', context=context)


@staff_member_required
def payment_records(request):
    payments = Payment.objects.all()
    context = {
        'payments': payments
    }
    return render(request, 'dashboard/payment_records.html', context=context)


@staff_member_required
def user_details(request, user_id):
    user = CustomUser.objects.filter(id=user_id).first()
    if user is None:
        raise Http404
    orders = Order.objects.filter(user=user)
    context = {
        'user': user,
        'orders': orders
    }
    return render(request, 'dashboard/user_details.html', context=context)


@staff_member_required
def import_users_from_login(request):
    login_users = CustomUser.objects.all()
    User = get_user_model()
    imported_users_count = 0
    for login_user in login_users:
        if not User.objects.filter(email=login_user.email).exists():
            User.objects.create_user(email=login_user.email, Phone_Num=login_user.Phone_Num, name=login_user.name)
            imported_users_count += 1
    messages.success(request, f"{imported_users_count} users imported from LOGIN app successfully.")
    return redirect('admin_dashboard')


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