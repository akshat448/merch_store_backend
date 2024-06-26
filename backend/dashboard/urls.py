from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="admin_dashboard"),
    path("import-users/", views.import_users_from_csv, name="import_users_from_csv"),
    path("orders-csv/<int:id>/", views.ordersCSV, name="orders_csv"),
    path("stop-orders/", views.stopOrders, name="stop_orders"),
    path("discount-codes/", views.discount_codes, name="discount_codes"),
    path(
        "discount-codes/create/",
        views.create_discount_code,
        name="create_discount_code",
    ),
    path(
        "discount-codes/edit/<int:code_id>/",
        views.edit_discount_code,
        name="edit_discount_code",
    ),
    path(
        "discount-codes/delete/<int:code_id>/",
        views.delete_discount_code,
        name="delete_discount_code",
    ),
    path("products/", views.products, name="products"),
    path("products/create/", views.create_product, name="create_product"),
    path("products/edit/<int:product_id>/", views.edit_product, name="edit_product"),
    path(
        "products/delete/<int:product_id>/", views.delete_product, name="delete_product"
    ),
    # path('scan_qr/', views.scan_qr, name='dashboard_scan_qr'),
]
