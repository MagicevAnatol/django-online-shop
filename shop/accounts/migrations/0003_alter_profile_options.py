# Generated by Django 5.0.6 on 2024-06-25 07:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_rename_alt_profile_avatar_alt_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="profile",
            options={"verbose_name": "Profile", "verbose_name_plural": "Profiles"},
        ),
    ]
