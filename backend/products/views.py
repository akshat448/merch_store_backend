from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Product, CartItem
from order.models import OrderItem
from .serializers import ProductSerializer, CartItemSerializer
from .permissions import IsAdmin


class AllProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_position = user.position

        # Filter products based on the user's position
        queryset = Product.objects.filter(for_user_positions__contains=[user_position], is_visible=True)
        serializer = ProductSerializer(queryset, many=True, context={'user': user})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductView(APIView):
    def get(self, request, product_id):
        user = request.user
        user_position = user.position

        product = Product.objects.filter(id=product_id).first()
        if not product or (user.is_authenticated and user_position not in product.for_user_positions) or not product.is_visible:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductSerializer(product, context={'user': user})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddToCart(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        product = Product.objects.filter(id=product_id).first()
        user = request.user
        user_position = user.position
        quantity = int(request.data.get('quantity', 1))

        if not product or user_position not in product.for_user_positions or CartItem.objects.filter(user=user, product=product).exists() or OrderItem.objects.filter(product=product, order__user=user).exclude(order__is_verified=False).exists() or not product.is_visible or not product.accept_orders:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if quantity > product.max_quantity:
            return Response({"error": "Quantity exceeds the maximum allowed."}, status=status.HTTP_400_BAD_REQUEST)

        printing_name = request.data.get('printing_name')
        size = request.data.get('size')
        image_url = request.data.get('image_url')

        if (product.is_name_required and printing_name is None) or (product.is_size_required and size is None) or (product.is_image_required and image_url is None):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        cart_item = CartItem(product=product, user=user, quantity=quantity, printing_name=printing_name, size=size, image_url=image_url)
        cart_item.save()
        return Response(status=status.HTTP_200_OK)


class ViewCart(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = CartItem.objects.filter(user=request.user)
        serializer = CartItemSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RemoveFromCart(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart_item_id = request.data.get("cart_item_id")
        cart_item = CartItem.objects.filter(id=cart_item_id).first()

        if not cart_item or cart_item.user != request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        cart_item.delete()
        return Response(status=status.HTTP_200_OK)
