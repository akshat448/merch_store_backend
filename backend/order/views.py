from django.shortcuts import get_object_or_404, redirect
from .models import Order, OrderItem
from discounts.models import DiscountCode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from .serializers import OrderSerializer
from django.db import transaction
import stripe
from django.conf import settings
from products.models import CartItem
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


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


class ApplyDiscountCode(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        user = request.user
        order = get_object_or_404(Order, id=order_id, user=user)
        code = request.data.get('discount_code')

        try:
            discount = DiscountCode.objects.get(code=code)
            if discount.is_valid():
                order.discount_code = discount
                order.save()
                discount.uses += 1
                discount.save()
                return Response({'detail': 'Discount code applied successfully!'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid or expired discount code.'}, status=status.HTTP_400_BAD_REQUEST)
        except DiscountCode.DoesNotExist:
            return Response({'detail': 'Discount code does not exist.'}, status=status.HTTP_400_BAD_REQUEST)



class PlaceOrder(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if cart_items.count() == 0:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = sum(float(item.product.price) for item in cart_items)

        # Check if a discount code is applied
        discount_code = request.data.get('discount_code')
        if discount_code:
            try:
                discount = DiscountCode.objects.get(code=discount_code)
                if discount.is_valid():
                    total_amount -= total_amount * (discount.discount_percentage / 100)
                    discount.uses += 1
                    discount.save()
            except DiscountCode.DoesNotExist:
                return Response({'error': 'Discount code not found'}, status=status.HTTP_400_BAD_REQUEST)

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

            # Create an Order instance
            order = Order.objects.create(user=user, amount=total_amount)
            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.product, printing_name=item.printing_name, size=item.size, image_url=item.image_url)
            cart_items.delete()  # Clear cart after order is placed

            return Response({'session_url': checkout_session.url}, status=status.HTTP_200_OK)
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise APIException(str(e))


"""
def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id)
    generate_qr_code(order)
    return render(request, 'order_confirmation.html', {'order': order})
"""