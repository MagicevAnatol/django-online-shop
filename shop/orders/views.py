from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer
from products.models import Cart, CartItem


class OrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(profile=request.user.profile)
        serializer = OrderSerializer(orders, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data={'products': request.data}, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            return Response({'orderId': order.id}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        order_id = request.data.get('orderId')
        order = Order.objects.get(id=order_id)
        serializer = OrderSerializer(order, data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            cart = Cart.objects.filter(profile=request.user.profile).first()
            if cart:
                CartItem.objects.filter(cart=cart).delete()
            return Response({'orderId': order.id}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)