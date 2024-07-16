# order/urls.py
from django.urls import path
from .views import AllOrders, OrderView, Checkout, ApplyDiscount

urlpatterns = [
    path("order/all/", AllOrders.as_view(), name="all_orders"),
    path("order/<int:order_id>/", OrderView.as_view(), name="order_view"),
    path("order/place/", Checkout.as_view(), name="place_order"),
    path("order/apply-discount/", ApplyDiscount.as_view(), name="apply_discount"),
    # path('orders/apply-discount/<int:order_id>/', ApplyDiscountCode.as_view(), name='apply_discount_code'),
]
