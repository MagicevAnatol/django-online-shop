from django.db import models

#
# class Category(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#
#     def __str__(self):
#         return self.name
#
#
# class Product(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     price = models.FloatField()
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self.name
