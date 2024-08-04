import qrcode
from io import BytesIO
from django.core.files import File
from .models import Order, Payment

def generate_qr_code(order):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    data = f"{order.id}|{order.payment.txnid}"
    qr.add_data(data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img_io = BytesIO()
    qr_img.save(qr_img_io)

    order.qr_code.save(f'order_{order.id}.png', File(qr_img_io), save=False)
    order.save()
