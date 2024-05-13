# Generated by Django 5.0.3 on 2024-05-13 19:20

from django.db import migrations


def main_jammy(apps, schema_editor):
    Target = apps.get_model("rainboard", "Target")
    Target.objects.update(main=False)
    Target.objects.filter(name="22.04").update(main=True)


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0082_update_targets"),
    ]

    operations = [
        migrations.RunPython(main_jammy),
    ]
