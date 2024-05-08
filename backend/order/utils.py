import qrcode
from io import BytesIO
from django.core.files import File
from .models import Order

def generate_qr_code(order):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(order.id)
    qr.make(fit=True)

    # Create an in-memory stream to save the image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img_io = BytesIO()
    qr_img.save(qr_img_io)

    # Save the QR code to the order
    order.qr_code.save(f'order_{order.id}.png', File(qr_img_io), save=False)
    order.save()
