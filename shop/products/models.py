from django.db import models


class Category(models.Model):
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    name = models.CharField(max_length=255)

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


def product_image_path(instance: "Product", filename: str) -> str:
    return f'products/product_{instance.id}/{filename}'


class Product(models.Model):
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    full_description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    free_delivery = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag)
    rating = models.FloatField(default=0.0)
    product_src = models.ImageField(upload_to=product_image_path)
    product_alt = models.CharField(max_length=255)

    def __str__(self):
        return self.title
