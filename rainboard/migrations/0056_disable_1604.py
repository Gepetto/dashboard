# Generated by Django 3.2 on 2021-04-29 15:08

from django.db import migrations


def disable_xenial(apps, schema_editor):
    Target = apps.get_model("rainboard", "Target")
    xenial = Target.objects.get(name="16.04")
    xenial.active = False
    xenial.save()
    Robotpkg = apps.get_model("rainboard", "Robotpkg")
    for rpkg in Robotpkg.objects.filter(
        project__slug__in=["eigenpy", "hpp-fcl", "pinocchio", "tsid", "crocoddyl"]
    ):
        rpkg.extended_target.add(xenial)


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0055_nullbooleanfield"),
    ]

    operations = [
        migrations.RunPython(disable_xenial),
    ]
