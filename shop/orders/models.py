from django.db import models
from products.models import Product
from accounts.models import Profile


class Order(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="orders"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_type = models.CharField(max_length=50)
    payment_type = models.CharField(max_length=50)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    products = models.ManyToManyField(
        Product, through="OrderProduct", related_name="orders"
    )

    def __str__(self):
        return f"Order {self.id} by {self.profile.full_name}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    number = models.CharField(max_length=8)
    name = models.CharField(max_length=50)
    month = models.CharField(max_length=2)
    year = models.CharField(max_length=4)
    code = models.CharField(max_length=3)

    def __str__(self):
        return f"Payment for Order {self.order.id}"
