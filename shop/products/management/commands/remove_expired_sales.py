from django.core.management.base import BaseCommand
from django.utils import timezone
from products.models import Sale

class Command(BaseCommand):
    help = 'Удаление продуктов, у которых закончился период распродажи'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        expired_sales = Sale.objects.filter(date_to__lt=today)
        count = expired_sales.count()
        expired_sales.delete()
        self.stdout.write(self.style.SUCCESS(f'Удалено {count} распродаж с истекшим периодом'))