# Generated by Django 3.2.5 on 2021-12-01 10:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0065_alter_robotpkg_extended_target"),
    ]

    operations = [
        migrations.AlterField(
            model_name="robotpkg",
            name="extended_target",
            field=models.ManyToManyField(blank=True, to="rainboard.Target"),
        ),
    ]
