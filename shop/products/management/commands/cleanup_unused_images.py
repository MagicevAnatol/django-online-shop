import os
from django.core.management.base import BaseCommand
from django.conf import settings

from products.models import Image, Product
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Удаляет неиспользуемые изображения товаров и профилей'

    def handle(self, *args, **kwargs):
        # Получаем все изображения товаров из базы данных
        all_product_images = Image.objects.all()
        used_image_paths = set()

        # Собираем пути всех используемых изображений товаров
        for image in all_product_images:
            if image.product_id:
                image_path = image.src.path
                if os.path.isfile(image_path):
                    used_image_paths.add(image_path)

        # Получаем все пути изображений профилей из базы данных
        all_profile_images = Profile.objects.values_list('avatar_src', flat=True)

        # Собираем пути всех используемых изображений профилей
        for image_path in all_profile_images:
            if image_path:
                full_path = os.path.join(settings.MEDIA_ROOT, image_path)
                if os.path.isfile(full_path):
                    used_image_paths.add(full_path)

        # Получаем все пути изображений на файловой системе
        media_root = settings.MEDIA_ROOT
        product_images_dir = os.path.join(media_root, 'products')
        profile_images_dir = os.path.join(media_root, 'profiles')
        all_file_paths = set()

        # Собираем все пути изображений товаров
        for root, _, files in os.walk(product_images_dir):
            for file in files:
                file_path = os.path.join(root, file)
                all_file_paths.add(file_path)

        # Собираем все пути изображений профилей
        for root, _, files in os.walk(profile_images_dir):
            for file in files:
                file_path = os.path.join(root, file)
                all_file_paths.add(file_path)

        # Находим неиспользуемые изображения
        used_image_paths = {os.path.normpath(path).lower() for path in used_image_paths}
        all_file_paths = {os.path.normpath(path).lower() for path in all_file_paths}
        unused_images = all_file_paths - used_image_paths
        # Удаляем неиспользуемые изображения
        for file_path in unused_images:
            try:
                # os.remove(file_path)
                self.stdout.write(self.style.SUCCESS(f'Удалено: {file_path}'))
            except OSError as e:
                self.stdout.write(self.style.ERROR(f'Ошибка при удалении {file_path}: {e}'))

        self.stdout.write(self.style.SUCCESS('Команда успешно выполнена'))