import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer, PaymentSerializer
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
        payment_type = request.data.get('paymentType')
        print(payment_type)

        order = Order.objects.get(id=order_id)
        serializer = OrderSerializer(order, data=request.data, context={'request': request})

        if serializer.is_valid():
            order = serializer.save()

            if payment_type == 'someone':
                fake_payment_data = {
                    "order": order.id,
                    "number": ''.join([str(random.randint(1, 9)) for _ in range(8)]),
                    "name": "Annoying Orange",
                    "month": "02",
                    "year": "2025",
                    "code": "123"
                }
                return Response({'orderId': order.id, 'payment': fake_payment_data},status=status.HTTP_200_OK)

            cart = Cart.objects.filter(profile=request.user.profile).first()
            if cart:
                CartItem.objects.filter(cart=cart).delete()

            return Response({'orderId': order.id}, status=status.HTTP_201_CREATED)

        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentView(APIView):

    def get(self, request, *args, **kwargs):
        print(request.data)
        print(request.query_params)
        return Response(request.data, status=status.HTTP_200_OK)

    def post(self, request, pk, *args, **kwargs):
        data = request.data.copy()
        data['order'] = pk
        serializer = PaymentSerializer(data=data)
        print(data)
        if serializer.is_valid():
            order = Order.objects.get(id=pk)
            order.status = "оплачено"
            order.save()
            payment = serializer.save()
            return Response(request.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

