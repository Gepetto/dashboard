# Generated by Django 5.1.4 on 2024-12-06 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gh", "0003_pushqueue"),
    ]

    operations = [
        migrations.AddField(
            model_name="pushqueue",
            name="retry",
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
