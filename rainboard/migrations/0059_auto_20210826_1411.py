# Generated by Django 3.2.5 on 2021-08-26 12:11

from django.db import migrations


def simple_robotics(apps, schema_editor):
    Namespace = apps.get_model('rainboard', 'Namespace')
    Namespace.objects.create(name='Simple Robotics', group=True)


class Migration(migrations.Migration):

    dependencies = [
        ('rainboard', '0058_drop_py3_debug'),
    ]

    operations = [
        migrations.RunPython(simple_robotics),
    ]
