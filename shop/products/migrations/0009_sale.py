# Generated by Django 5.0.6 on 2024-07-05 18:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_cart_session_key_alter_cart_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sale_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_from', models.DateField()),
                ('date_to', models.DateField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
        ),
    ]