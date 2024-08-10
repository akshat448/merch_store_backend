from __future__ import absolute_import, unicode_literals
import logging


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)


def send_order_completion_email(order_id, user_name, user_email):
    subject = "Your order has been delivered successfully."

    context = {"name": user_name, "id": order_id}
    try:
        html_message = render_to_string(
            "dashboard/send_order_completion_email.html", context
        )
        msg = strip_tags(html_message)
        send_mail(
            subject,
            msg,
            settings.EMAIL_HOST_USER,
            (user_email,),
            html_message=html_message,
            fail_silently=False,
        )
        return logger.info("Order delivery confirmation mail sent to {user_email}")
    except Exception as e:
        logger.error(f"Error sending order delivery confirmation email: {e}")
        raise
