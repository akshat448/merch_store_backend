from .models import Order, OrderItem
from discounts.models import DiscountCode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import OrderSerializer
from django.db import transaction
from products.models import CartItem


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


class Checkout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"detail": "No items in cart."}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        discount_code = request.data.get("discount_code", None)
        discount_percentage = 0
        updated_amount = total_amount

        if discount_code:
            try:
                discount = DiscountCode.objects.get(code=discount_code)
                if discount.is_valid() and user in discount.roles_allowed.all():
                    discount_percentage = discount.discount_percentage
                    updated_amount -= total_amount * (discount_percentage / 100)
                else:
                    return Response({"detail": "Invalid or expired discount code."}, status=status.HTTP_400_BAD_REQUEST)
            except DiscountCode.DoesNotExist:
                return Response({"detail": "Discount code does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order = Order.objects.create(user=user, amount=total_amount)
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    printing_name=item.printing_name,
                    size=item.size,
                    image_url=item.image_url,
                )
            cart_items.delete()

        if discount_code:
            order.discount_code = discount
            order.save()

        serializer = OrderSerializer(order)
        return Response(
            {
                "order": serializer.data,
                "total_amount": total_amount,
                "updated_amount": updated_amount,
                "discount_percentage": discount_percentage,
            },
            status=status.HTTP_201_CREATED
        )


"""
def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id)
    generate_qr_code(order)
    return render(request, 'order_confirmation.html', {'order': order})
"""