import os
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Image, Product


class Command(BaseCommand):
    help = "Удаляет неиспользуемые изображения товаров"

    def handle(self, *args, **kwargs):
        # Получаем все изображения из базы данных
        all_images = Image.objects.all()
        used_image_paths = set()

        # Собираем пути всех используемых изображений
        for image in all_images:
            if image.product_id:
                used_image_paths.add(image.src.path)

        # Получаем все пути изображений на файловой системе
        media_root = settings.MEDIA_ROOT
        product_images_dir = os.path.join(media_root, "products")
        all_file_paths = set()

        for root, _, files in os.walk(product_images_dir):
            for file in files:
                file_path = os.path.join(root, file)
                all_file_paths.add(file_path)

        # Находим неиспользуемые изображения
        unused_images = all_file_paths - used_image_paths

        # Удаляем неиспользуемые изображения
        for file_path in unused_images:
            try:
                os.remove(file_path)
                self.stdout.write(self.style.SUCCESS(f"Удалено: {file_path}"))
            except OSError as e:
                self.stdout.write(
                    self.style.ERROR(f"Ошибка при удалении {file_path}: {e}")
                )

        self.stdout.write(self.style.SUCCESS("Команда успешно выполнена"))
