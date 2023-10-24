# Generated by Django 4.2.6 on 2023-10-24 08:49

from django.db import migrations


def drop_1804(apps, schema_editor):
    robotpkg = apps.get_model("rainboard", "Robotpkg")
    for rpkg in robotpkg.objects.filter(
        project__slug__in=["eigenpy", "hpp-fcl", "pinocchio"],
    ):
        rpkg.extended_target.clear()


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0077_alter_image_image"),
    ]

    operations = [
        migrations.RunPython(drop_1804),
    ]
