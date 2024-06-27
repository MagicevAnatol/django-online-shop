from django.db import models
from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Category(models.Model):
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    name = models.CharField(max_length=255)
    image_src = models.ImageField(upload_to='categories/', default='default.jpg')
    image_alt = models.CharField(max_length=255, default='Default alt text')

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"

    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image_src = models.ImageField(upload_to='subcategories/', default='default.jpg')
    image_alt = models.CharField(max_length=255, default='Default alt text')

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Specification(models.Model):
    class Meta:
        verbose_name = "Specification"
        verbose_name_plural = "Specifications"

    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    product = models.ForeignKey('Product', related_name='specifications', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}: {self.value}"


class Review(models.Model):
    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    author = models.CharField(max_length=255)
    email = models.EmailField()
    text = models.TextField()
    rate = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey('Product', related_name='reviews', on_delete=models.CASCADE)

    def __str__(self):
        return f"Review by {self.author} - {self.rate} stars"


@receiver(post_save, sender=Review)
def update_product_rating_on_save(sender, instance, **kwargs):
    instance.product.update_rating()


@receiver(post_delete, sender=Review)
def update_product_rating_on_delete(sender, instance, **kwargs):
    instance.product.update_rating()


def product_image_path(instance: "Image", filename: str) -> str:
    return f'products/product_{instance.product_id}/{filename}'


class Image(models.Model):
    product = models.ForeignKey('Product', related_name='images', on_delete=models.CASCADE)
    src = models.ImageField(upload_to=product_image_path)
    alt = models.CharField(max_length=255)

    def __str__(self):
        return self.alt


class Product(models.Model):
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, related_name='products', on_delete=models.SET_NULL,
                                    null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    full_description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    free_delivery = models.BooleanField(default=False)
    limited = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag)
    rating = models.FloatField(default=0.0)

    def update_rating(self):
        average_rating = self.reviews.aggregate(Avg('rate'))['rate__avg']
        self.rating = round(average_rating, 2) if average_rating is not None else 0
        self.save()

    def __str__(self):
        return self.title
