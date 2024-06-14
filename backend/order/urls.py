# order/urls.py
from django.urls import path
from .views import AllOrders, OrderView, PlaceOrder, ApplyDiscountCode

urlpatterns = [
    path('orders/', AllOrders.as_view(), name='all_orders'),
    path('orders/<int:order_id>/', OrderView.as_view(), name='order_view'),
    path('orders/place/', PlaceOrder.as_view(), name='place_order'),
    path('orders/apply-discount/<int:order_id>/', ApplyDiscountCode.as_view(), name='apply_discount_code'),
]
