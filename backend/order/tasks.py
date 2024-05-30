from __future__ import absolute_import, unicode_literals
import logging

from backend.celery import app

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)

@app.task(name='send_order_confirmation_email')
def send_order_confirmation_email(order_id, order_amount, products, user_name, user_email):
    subject = "Thank you for your purchase. Here's the confirmation of your order."
    
    context = {
        'name': user_name,
        'id': order_id,
        'items': ', '.join(name for name in products),
        'amount': order_amount
    }
    try:
        html_message = render_to_string('dashboard/email_order_success.html', context)
        msg = strip_tags(html_message)
        send_mail(subject, msg, settings.EMAIL_HOST_USER, (user_email, ), html_message=html_message, fail_silently=False)
        return f"Order confirmation mail sent to {user_email}"
    except Exception as e:
        logger.error(f"Error sending order confirmation email: {e}")
        raise

@app.task(name='send_order_failure_email')
def send_order_failure_email(order_id, user_name, user_email):
    subject = "We couldn't process your order."

    context = {
        'name': user_name,
        'id': order_id
    }
    try:
        html_message = render_to_string('dashboard/email_order_failed.html', context=context)
        msg = strip_tags(html_message)
        send_mail(subject, msg, settings.EMAIL_HOST_USER, (user_email, ), html_message=html_message, fail_silently=False)
        return f"Order failure mail sent to {user_email}"
    except Exception as e:
        logger.error(f"Error sending order failure email: {e}")
        raise