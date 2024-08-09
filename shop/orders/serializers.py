from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers
from .models import Order, OrderProduct, Payment
from products.serializers import TagSerializer, ImageSerializer
from products.models import Product, Cart, CartItem, Sale


def validate_card_number(number):
    if len(number) > 8:
        raise ValidationError("Номер должен быть не длиннее восьми цифр.")
    if int(number) % 2 != 0 or number.endswith("0"):
        raise ValidationError("Номер должен быть чётным и не заканчиваться на ноль.")


class OrderProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="product.id")
    category = serializers.IntegerField(source="product.category.id")
    price = serializers.SerializerMethodField()
    count = serializers.IntegerField()
    date = serializers.DateTimeField(source="product.date")
    title = serializers.CharField(source="product.title")
    description = serializers.CharField(source="product.description")
    freeDelivery = serializers.BooleanField(source="product.free_delivery")
    images = ImageSerializer(source="product.images", many=True, read_only=True)
    tags = TagSerializer(source="product.tags", many=True)
    reviews = serializers.IntegerField(source="product.reviews.count")
    rating = serializers.FloatField(source="product.rating")

    class Meta:
        model = OrderProduct
        fields = [
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
        ]

    def get_price(self, obj):
        today = timezone.now().date()
        active_sale = Sale.objects.filter(
            product=obj.product, date_from__lte=today, date_to__gte=today
        ).first()
        if active_sale:
            return active_sale.sale_price
        return obj.product.price


class OrderCreateSerializer(serializers.ModelSerializer):
    products = serializers.ListField()

    class Meta:
        model = Order
        fields = ["products"]

    def create(self, validated_data):
        products_data = validated_data.pop("products")
        profile = self.context["request"].user.profile
        order = Order.objects.create(profile=profile, status="в доработке")
        total_cost = 0

        for product_data in products_data:
            product = Product.objects.get(id=product_data["id"])
            today = timezone.now().date()
            active_sale = Sale.objects.filter(
                product=product, date_from__lte=today, date_to__gte=today
            ).first()
            if active_sale:
                price = active_sale.sale_price
            else:
                price = product.price
            count = product_data["count"]
            OrderProduct.objects.create(order=order, product=product, count=count)
            total_cost += price * count

        order.total_cost = total_cost
        order.save()
        return order


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(
        source="orderproduct_set", many=True, read_only=True
    )
    createdAt = serializers.DateTimeField(source="created_at")
    fullName = serializers.CharField(source="profile.full_name", read_only=True)
    email = serializers.EmailField(source="profile.email", read_only=True)
    phone = serializers.CharField(source="profile.phone", read_only=True)
    deliveryType = serializers.CharField(source="delivery_type")
    paymentType = serializers.CharField(source="payment_type")
    totalCost = serializers.DecimalField(
        source="total_cost", max_digits=10, decimal_places=2
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
        ]

    def update(self, instance, validated_data):
        instance.delivery_type = validated_data.get("delivery_type")
        instance.city = validated_data.get("city")
        instance.address = validated_data.get("address")
        instance.payment_type = validated_data.get("payment_type")
        if instance.delivery_type == "express":
            instance.total_cost += Decimal("500.00")
        instance.status = "ожидает оплаты"

        instance.save()
        return instance


class PaymentSerializer(serializers.ModelSerializer):
    number = serializers.CharField(validators=[validate_card_number])

    class Meta:
        model = Payment
        fields = ["order", "number", "name", "month", "year", "code"]
