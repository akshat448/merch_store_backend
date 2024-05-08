from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard),
    path('payment_records/', views.payment_records, name='admin_payment_records'),
    path('user_details/<int:user_id>/', views.user_details, name='admin_user_details'),
    path('import_users_from_login/', views.import_users_from_login, name='admin_import_users_from_login'),
    path('stopOrders/', views.stopOrders, name='admin_stop_orders'),
    #path('scan_qr/', views.scan_qr, name='admin_scan_qr'),
]
