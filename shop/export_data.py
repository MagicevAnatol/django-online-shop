import os
import sys
import json
from django.core.management import call_command
from io import StringIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')

import django
django.setup()

fixtures_dir = 'fixtures'
if not os.path.exists(fixtures_dir):
    os.makedirs(fixtures_dir)

# Экспорт данных в файлы JSON
export_order = [
    'auth.user',
    'products.category',
    'products.subcategory',
    'products.product',
    'products.cart',
    'accounts.profile',
    'products.tag',
    'products.product_tags',
    'products.image',
    'products.review',
    'products.cartitem',
    'products.sale',
    'orders.order',
    'orders.orderproduct',
    'orders.payment',
    'products.specification',
]

for model in export_order:
    print(f"Exporting {model}...")
    output = StringIO()
    try:
        call_command('dumpdata', model, stdout=output, indent=2)
        with open(f'{fixtures_dir}/{model.replace(".", "_")}.json', 'w', encoding='utf-8') as f:
            f.write(output.getvalue())
    except Exception as e:
        print(f"Error exporting {model}: {e}")