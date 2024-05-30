from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    path('import-users/', views.import_users_from_login, name='import_users_from_login'),
    path('orders-csv/<int:id>/', views.ordersCSV, name='orders_csv'),
    path('stop-orders/', views.stopOrders, name='stop_orders'),
    #path('scan_qr/', views.scan_qr, name='dashboard_scan_qr'),
]
