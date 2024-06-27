# Generated by Django 5.0.6 on 2024-06-27 16:41

import django.db.models.deletion
import products.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_product_limited'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='product_alt',
        ),
        migrations.RemoveField(
            model_name='product',
            name='product_src',
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('src', models.ImageField(upload_to=products.models.product_image_path)),
                ('alt', models.CharField(max_length=255)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.product')),
            ],
        ),
    ]
