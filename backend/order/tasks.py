from __future__ import absolute_import, unicode_literals
import logging

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)


def send_order_success_email(order_id, total, items, name, qr_code, user_email):
    subject = "Thank you for your purchase. Here's the confirmation of your order."

    context = {
        "name": name,
        "qr_code": qr_code,
        "id": order_id,
        "items": items,
        "total": total,
    }
    try:
        html_message = render_to_string("dashboard/email_success_qr.html", context)
        msg = strip_tags(html_message)
        send_mail(
            subject,
            msg,
            settings.EMAIL_HOST_USER,
            (user_email,),
            html_message=html_message,
            fail_silently=False,
        )
        return logger.info("Order success mail sent to {user_email}")
    except Exception as e:
        logger.error(f"Error sending order success email: {e}")
        raise
