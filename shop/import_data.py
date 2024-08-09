import os
import sys
from django.core.management import call_command
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shop.settings")

import django

django.setup()

# Порядок загрузки данных для импорта
import_order = [
    "auth_user",
    "accounts_profile",
    "products_category",
    "products_subcategory",
    "products_tag",
    "products_product",
    "products_product_tags",
    "products_image",
    "products_review",
    "products_specification",
    "products_cart",
    "products_cartitem",
    "products_sale",
    "orders_order",
    "orders_orderproduct",
    "orders_payment",
]

fixtures_dir = "fixtures"

# Отключение проверок целостности
with connection.constraint_checks_disabled():
    for fixture in import_order:
        print(f"Importing {fixture}...")
        try:
            call_command("loaddata", os.path.join(fixtures_dir, fixture))
        except Exception as e:
            print(f"Error importing {fixture}: {e}")

# Включение проверок целостности
connection.check_constraints()
