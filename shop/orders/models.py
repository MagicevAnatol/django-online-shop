from django.db import models
# from django.contrib.auth.models import User
# from products.models import Product
#
#
# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     total_price = models.FloatField()
#     status = models.CharField(max_length=50)
#
#     def __str__(self):
#         return f"Order {self.id} by {self.user.username}"
#
#
# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#     price = models.FloatField()
#
#     def __str__(self):
#         return f"{self.quantity} of {self.product.name}"
