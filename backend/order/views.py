import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse
from .models import Order, OrderItem
from products.models import CartItem
from .serializers import OrderSerializer
from .utils import generate_qr_code
from django.shortcuts import render
from datetime import datetime

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

class AllOrders(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = Order.objects.filter(user=user)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        user = request.user
        order = Order.objects.filter(id=order_id, user=user).first()
        if order is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PlaceOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if cart_items.count() == 0:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = sum(float(item.product.price) for item in cart_items)

        # Create a Stripe checkout session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': 'Cart Items',
                        },
                        'unit_amount': int(total_amount * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('checkout_success')),
                cancel_url=request.build_absolute_uri(reverse('checkout_cancel')),
            )

            # Return the session URL to the frontend
            return Response({'session_url': checkout_session.url}, status=status.HTTP_200_OK)
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

"""
def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id)
    generate_qr_code(order)
    return render(request, 'order_confirmation.html', {'order': order})
"""