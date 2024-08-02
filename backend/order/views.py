import hashlib
import requests
import time
import urllib.parse
from rest_framework.views import APIView
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.db import transaction

from .models import Order, OrderItem, Payment
from .serializers import OrderSerializer
from discounts.models import DiscountCode
from products.models import CartItem

def generateHash(params, salt):
        hashString = (
            params["key"] + "|" +
            params["txnid"] + "|" +
            params["amount"] + "|" +
            params["productinfo"] + "|" +
            params["firstname"] + "|" +
            params["email"] + "|" +
            params.get("udf1", "") + "|" +
            params.get("udf2", "") + "|" +
            params.get("udf3", "") + "|" +
            params.get("udf4", "") + "|" +
            params.get("udf5", "") + "||||||" +
            salt
        )
        return hashlib.sha512(hashString.encode('utf-8')).hexdigest().lower()



class AllOrders(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = Order.objects.filter(user=user)
        serializer = OrderSerializer(queryset, many=True, context={'user': user})
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        user = request.user
        order = Order.objects.filter(id=order_id, user=user).first()
        if order is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = OrderSerializer(order, context={'user': user})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ApplyDiscount(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        discount_code = request.data.get("discount_code", None)

        if not discount_code:
            return Response(
                {"detail": "Discount code is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return Response(
                {"detail": "No items in cart."}, status=status.HTTP_400_BAD_REQUEST
            )

        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        if discount_code == "NO_DISCOUNT":
            return Response(
                {
                    "total_amount": total_amount,
                    "discount_percentage": 0,
                    "updated_amount": total_amount,
                },
                status=status.HTTP_200_OK,
            )

        try:
            discount = DiscountCode.objects.get(code=discount_code)
            if discount.is_valid() and user.position in discount.for_user_positions:
                discount_percentage = discount.discount_percentage
                updated_amount = (total_amount) - (total_amount) * (
                    discount_percentage / 100
                )
                return Response(
                    {
                        "total_amount": float(total_amount),
                        "discount_percentage": float(discount_percentage),
                        "updated_amount": float(updated_amount),
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"detail": "Invalid or expired discount code."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except DiscountCode.DoesNotExist:
            return Response(
                {"detail": "Discount code does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Checkout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return Response(
                {"detail": "No items in cart."}, status=status.HTTP_400_BAD_REQUEST
            )

        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        updated_amount = total_amount

        discount_code = request.data.get("discount_code", None)

        if discount_code:
            try:
                discount = DiscountCode.objects.get(code=discount_code)
                if discount.is_valid() and user.position in discount.for_user_positions:
                    discount_percentage = discount.discount_percentage
                    updated_amount = (total_amount) - (total_amount) * (
                        discount_percentage / 100
                    )
                else:
                    return Response(
                        {"detail": "Invalid or expired discount code."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except DiscountCode.DoesNotExist:
                return Response(
                    {"detail": "Discount code does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        with transaction.atomic():
            #order = Order.objects.create(user=user, updated_amount=updated_amount, total_amount=total_amount)
            order = Order.objects.create(user=user, updated_amount=updated_amount)
            #order.generate_qr_code()
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    printing_name=item.printing_name,
                    size=item.size,
                    image_url=item.image_url,
                    quantity=item.quantity,
                )
            cart_items.delete()

        if discount_code:
            order.discount_code = discount
            order.save()

        serializer = OrderSerializer(order, context={'user': user})
        return Response(
            {
                "order": serializer.data,
                "total_amount": float(total_amount),
                "updated_amount": float(updated_amount),
                "discount_percentage": float(
                    discount.discount_percentage if discount_code else 0
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class Paymentiew(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, order_id):
        user = request.user
        try:
            order = Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        key = settings.PAYU_MERCHANT_KEY
        salt = settings.PAYU_MERCHANT_SALT
        txnid = str(order.id) + str(int(time.time() * 1000))
        amount = "{:.2f}".format(float(order.updated_amount))
        productinfo = "Order_" + str(order.id)
        firstname = str(user.name.split()[0] if ' ' in user.name else user.name)
        email = str(user.email)
        phone = str(user.phone_no)
        surl = settings.PAYU_SUCCESS_URL
        furl = settings.PAYU_FAILURE_URL

        # PayU payload as a dictionary
        payload = {
            "key": key,
            "txnid": txnid,
            "amount": amount,
            "firstname": firstname,
            "email": email,
            "phone": phone,
            "productinfo": productinfo,
            "surl": surl,
            "furl": furl,
            "udf1": "","udf2": "","udf3": "","udf4": "","udf5": ""
        }
        
        # Generate the hash
        hashValue = generateHash(payload, salt)
        
        # Add the hash to the parameter map
        payload["hash"] = hashValue
        
        return Response(payload, status=status.HTTP_200_OK)
        """
        # Encode the parameters for use in the URL
        payload = urllib.parse.urlencode(payload)
        
        # Build the URL for the PayU API request
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post("https://test.payu.in/_payment", data=payload, headers=headers)

        # Check if the response from PayU is successful
        if response.status_code == 200:
            response_content = response.text
            print(response_content)
            # Check for known error indicators in the response content
            if "Invalid amount" in response_content:
                return Response({"detail": "Invalid amount error from PayU."}, status=status.HTTP_400_BAD_REQUEST)
            elif "Some problem occurred" in response_content:
                return Response({"detail": "Some problem occurred with PayU."}, status=status.HTTP_400_BAD_REQUEST)

            # Create Payment instance
            Payment.objects.create(order=order, transaction_id=txnid, paid_amount=order.updated_amount, status='pending')
            return redirect(response.url)
        else:
            return Response({"detail": "Failed to initiate payment with PayU."}, status=status.HTTP_400_BAD_REQUEST)
        """

class PayuSuccessView(APIView):
    def post(self, request):
        txnid = request.data.get('txnid')
        status = request.data.get('status')
        
        try:
            payment = Payment.objects.get(transaction_id=txnid)
            payment.status = status
            payment.save()

            if status == 'success':
                payment.order.is_verified = True
                payment.order.save()

            return Response({"detail": "Payment processed successfully."}, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response({"detail": "Payment record not found."}, status=status.HTTP_404_NOT_FOUND)


class PayuFailureView(APIView):
    def post(self, request):
        txnid = request.data.get('txnid')
        
        try:
            payment = Payment.objects.get(transaction_id=txnid)
            payment.status = 'failure'
            payment.save()

            return Response({"detail": "Payment failed."}, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response({"detail": "Payment record not found."}, status=status.HTTP_404_NOT_FOUND)

"""def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_confirmation.html', {'order': order})
"""