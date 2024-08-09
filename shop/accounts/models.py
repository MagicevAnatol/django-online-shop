from django.db import models
from django.contrib.auth.models import User


# Функция для указания пути загрузки аватара
def avatar_image_path(instance: "Profile", filename: str) -> str:
    return f"profiles/user_{instance.user.pk}/avatar/{filename}"


# Основная модель пользователя
class Profile(models.Model):
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar_src = models.ImageField(upload_to=avatar_image_path, blank=True, null=True)
    avatar_alt = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.full_name
