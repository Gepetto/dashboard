# Generated by Django 4.2.2 on 2023-06-05 16:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "rainboard",
            "0076_alter_project_cmake_name_alter_project_description_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="image",
            name="image",
            field=models.CharField(blank=True, default="", max_length=12),
        ),
    ]
