from django.db import models
from products.models import Product
from accounts.models import Profile


class Order(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_type = models.CharField(max_length=50)
    payment_type = models.CharField(max_length=50)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    products = models.ManyToManyField(Product, related_name='orders')

    def __str__(self):
        return f'Order {self.id} by {self.profile.full_name}'
