# Generated by Django 2.2 on 2019-08-13 12:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0036_update_distros"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="has_python",
            field=models.BooleanField(default=True),
        ),
    ]
