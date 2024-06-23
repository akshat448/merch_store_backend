from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, StreamingHttpResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
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
import json
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
    amount_received = (
        Order.objects.filter(is_verified=True).aggregate(total=Sum("amount"))["total"]
        or 0
    )
    unsuccessful_orders = Order.objects.filter(is_verified=False).count()
    pending_orders = Order.objects.filter(is_verified=None).count()
    # items_ordered = OrderItem.objects.all().aggregate(total=Sum('quantity'))['total'] or 0
    items_ordered = 0

    items = []
    products = Product.objects.all()
    for product in products:
        orders_count = OrderItem.objects.filter(
            product=product, order__is_verified=True
        ).count()
        item = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "orders_count": orders_count,
        }
        items.append(item)

    users = CustomUser.objects.all()
    user_orders = {user: Order.objects.filter(user=user) for user in users}
    payments = Payment.objects.all()

    context = {
        "amount_received": amount_received,
        "items_ordered": items_ordered,
        "unsuccessful_orders": unsuccessful_orders,
        "pending_orders": pending_orders,
        "items": items,
        "productsCount": len(items),
        "user_orders": user_orders,
        "payments": payments,
    }

    return render(request, "dashboard/dashboard.html", context=context)


@staff_member_required
def import_users_from_csv(request):
    if request.method == "GET":
        return render(request, "dashboard/import_users.html")
    csv_file = request.FILES["file"]
    if not csv_file.name.endswith(".csv"):
        messages.error(request, "File is not a CSV file.")
        return redirect("/dashboard/")
    users = []
    try:
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)
        for row in reader:
            user = get_user_model()(
                email=row["email"],
                phone_no=row["phone_no"],
                name=row["name"],
                position=row["position"],
            )
            users.append(user)
    except Exception as e:
        messages.error(request, f"Error reading CSV file: {e}")
        return redirect("/dashboard/")
    get_user_model().objects.bulk_create(users)
    messages.success(request, "Users imported successfully.")
    return redirect("/dashboard/")


@staff_member_required
def discount_codes(request):
    discount_codes = DiscountCode.objects.all().order_by("-created_at")
    return render(
        request,
        "dashboard/discount_codes.html",
        {"discount_codes": discount_codes},
    )


@staff_member_required
def create_discount_code(request):
    if request.method == "POST":
        post = request.POST.copy()
        is_custom = post.get("custom", False)
        if is_custom == "on":
            post["custom"] = True
        else:
            post["custom"] = False
            post["code"] = "custom"
        request.POST = post
        form = DiscountCodeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Discount code created successfully.")
        else:
            messages.error(request, "Invalid data. Please correct the errors.")
        return redirect("/discount-codes")

    else:

        form = DiscountCodeForm()
    return render(request, "dashboard/discount_codes.html", {"form": form})


@staff_member_required
def edit_discount_code(request, code_id):
    discount_code = get_object_or_404(DiscountCode, id=code_id)

    if request.method == "POST":
        post = request.POST.copy()
        is_custom = post.get("custom", False)
        if is_custom == "on":
            post["custom"] = True
        else:
            post["custom"] = False
            if not post["code"]:
                post["code"] = "custom"
        request.POST = post
        form = DiscountCodeForm(request.POST, instance=discount_code)
        if form.is_valid():
            form.save()
            messages.success(request, "Discount code updated successfully.")
        else:
            messages.error(request, "Invalid data. Please correct the errors.")
        return redirect("/discount-codes")

    else:
        form = DiscountCodeForm(instance=discount_code)
        return render(request, "dashboard/discount_codes.html", {"form": form})


@staff_member_required
def delete_discount_code(request, code_id):
    discount_code = get_object_or_404(DiscountCode, id=code_id)
    discount_code.delete()
    messages.success(request, "Discount code deleted successfully.")
    return redirect("/discount-codes")


class Echo:
    def write(self, value):
        return value


@staff_member_required
def ordersCSV(request, id):
    if request.method == "GET":
        raise Http404
    product = Product.objects.filter(id=id).first()
    if product is None:
        raise Http404
    order_items = OrderItem.objects.filter(
        product=product, order__is_verified=True
    ).all()
    rows = []
    first_row = ["Name", "email id", "Phone Number", "position"]
    if product.is_size_required:
        first_row.append("Size")
    if product.is_name_required:
        first_row.append("Printing Name")
    if product.is_image_required:
        first_row.append("Image URL")
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
        content_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{product.name}_orders.csv"'
        },
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
    messages.success(request, "Stopped receiving orders and cleared all carts")
    return redirect("/dashboard")


@staff_member_required
def products(request):
    products = Product.objects.all()
    return render(request, "dashboard/products.html", {"products": products})


@staff_member_required
def create_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        is_size_required = request.POST.get("is_size_required", False) == "on"
        is_name_required = request.POST.get("is_name_required", False) == "on"
        is_image_required = request.POST.get("is_image_required", False) == "on"
        accept_orders = request.POST.get("accept_orders", False) == "on"
        description = request.POST.get("description")
        image1 = request.FILES.get("image1")
        image2 = request.FILES.get("image2")
        size_chart_image = request.FILES.get("size_chart_image")

        product = Product(
            name=name,
            price=price,
            is_size_required=is_size_required,
            is_name_required=is_name_required,
            is_image_required=is_image_required,
            accept_orders=accept_orders,
            description=description,
            image1=image1,
            image2=image2,
            size_chart_image=size_chart_image,
        )
        product.save()
        messages.success(request, "Product created successfully.")
        return redirect("/products")
    return render(request, "dashboard/products.html")


@staff_member_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        print(request.POST)
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.is_size_required = request.POST.get("is_size_required", False) == "on"
        product.is_name_required = request.POST.get("is_name_required", False) == "on"
        product.is_image_required = request.POST.get("is_image_required", False) == "on"
        product.accept_orders = request.POST.get("accept_orders", False) == "on"
        product.description = request.POST.get("description")
        product.image1 = request.FILES.get("image1") or product.image1
        product.image2 = request.FILES.get("image2") or product.image2
        product.size_chart_image = (
            request.FILES.get("size_chart_image") or product.size_chart_image
        )

        product.save()
        messages.success(request, "Product updated successfully.")
        return redirect("/products")
    return render(request, "dashboard/products.html")


@staff_member_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect("/products")


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
