# Generated by Django 3.2.4 on 2021-06-08 16:47

from django.db import migrations, models


def pal_private(apps, schema_editor):
    Target = apps.get_model("rainboard", "Target")
    Target.objects.filter(name__in=["dubnium", "erbium", "ferrum"]).update(public=False)


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0056_disable_1604"),
    ]

    operations = [
        migrations.AddField(
            model_name="target",
            name="public",
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(pal_private),
    ]
