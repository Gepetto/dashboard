# Generated by Django 3.2 on 2021-04-29 15:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0053_ferrum"),
    ]

    operations = [
        migrations.AddField(
            model_name="robotpkg",
            name="extended_target",
            field=models.ManyToManyField(to="rainboard.Target"),
        ),
    ]
