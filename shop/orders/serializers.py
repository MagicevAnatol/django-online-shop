from decimal import Decimal

from rest_framework import serializers
from .models import Order
from products.serializers import TagSerializer, ImageSerializer
from products.models import Product, Cart, CartItem


class OrderProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    count = serializers.SerializerMethodField()
    images = ImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True)
    reviews = serializers.IntegerField(source='reviews.count')
    freeDelivery = serializers.BooleanField(source='free_delivery')

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'price', 'count', 'date', 'title', 'description',
            'freeDelivery', 'images', 'tags', 'reviews', 'rating'
        ]

    def get_count(self, obj):
        user = self.context['request'].user

        cart = Cart.objects.filter(profile=user.profile).first()

        if cart:
            cart_item = CartItem.objects.filter(cart=cart, product=obj).first()
            if cart_item:
                return cart_item.count
        return 0


class OrderCreateSerializer(serializers.ModelSerializer):
    products = serializers.ListField()

    class Meta:
        model = Order
        fields = ['products']

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        profile = self.context['request'].user.profile
        order = Order.objects.create(profile=profile, status="в доработке")
        total_cost = 0
        print(products_data)
        for product_data in products_data:
            print(product_data)
            product = Product.objects.get(id=product_data['id'])
            order.products.add(product)
            total_cost += product_data['price'] * product_data['count']
        order.total_cost = total_cost
        order.save()
        return order


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, read_only=True)
    createdAt = serializers.DateTimeField(source='created_at')
    fullName = serializers.CharField(source='profile.full_name', read_only=True)
    email = serializers.EmailField(source='profile.email', read_only=True)
    phone = serializers.CharField(source='profile.phone', read_only=True)
    deliveryType = serializers.CharField(source="delivery_type")
    paymentType = serializers.CharField(source="payment_type")
    totalCost = serializers.DecimalField(source="total_cost", max_digits=10, decimal_places=2)

    class Meta:
        model = Order
        fields = [
            'id', 'createdAt', 'fullName', 'email', 'phone', 'deliveryType', 'paymentType',
            'totalCost', 'status', 'city', 'address', 'products'
        ]

    def update(self, instance, validated_data):
        instance.delivery_type = validated_data.get('delivery_type')
        instance.city = validated_data.get('city')
        instance.address = validated_data.get('address')
        instance.payment_type = validated_data.get('payment_type')
        if instance.delivery_type == 'express':
            instance.total_cost += Decimal('500.00')
        instance.status = 'ожидает оплаты'

        instance.save()
        return instance
