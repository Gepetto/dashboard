# Generated by Django 2.1.5 on 2019-02-11 16:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0028_image_allow_failure"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="suffix",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
    ]
