# Generated by Django 2.0.5 on 2018-06-19 09:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0015_debug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="robotpkg",
            name="homepage",
            field=models.URLField(blank=True, null=True),
        ),
    ]
