# Generated by Django 4.2 on 2023-04-05 11:27

from django.db import migrations


def drop_xenial(apps, schema_editor):
    target = apps.get_model("rainboard", "Target")
    robotpkg = apps.get_model("rainboard", "Robotpkg")
    xenial = target.objects.get(name="16.04")
    for rpkg in robotpkg.objects.filter(
        project__slug__in=["eigenpy", "hpp-fcl", "pinocchio", "tsid", "crocoddyl"],
    ):
        rpkg.extended_target.remove(xenial)


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0070_project_min_python_major"),
    ]

    operations = [
        migrations.RunPython(drop_xenial),
    ]
