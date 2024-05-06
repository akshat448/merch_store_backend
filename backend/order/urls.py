from django.urls import path
from .views import AllOrders, OrderView, PlaceOrder

app_name = 'order'

urlpatterns = [
    path('all/', AllOrders.as_view(), name='all_orders'),
    path('<slug:order_id>/', OrderView.as_view(), name='order_details'),
    path('place_order/', PlaceOrder.as_view(), name='place_order'),
]
