# Generated by Django 3.0.9 on 2020-08-06 08:33

from django.db import migrations


def add_targets(apps, schema_editor):
    Target = apps.get_model("rainboard", "Target")
    Target.objects.create(name="buster")


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0049_project_ccache"),
    ]

    operations = [
        migrations.RunPython(add_targets),
    ]
