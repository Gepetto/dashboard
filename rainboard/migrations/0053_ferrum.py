# Generated by Django 3.0.13 on 2021-03-04 12:28

from django.db import migrations


def erbium_to_ferrum(apps, schema_editor):
    Target = apps.get_model('rainboard', 'Target')
    Target.objects.filter(name='erbium').update(active=False)
    Target.objects.create(name='ferrum')


class Migration(migrations.Migration):

    dependencies = [
        ('rainboard', '0052_centos7'),
    ]

    operations = [
        migrations.RunPython(erbium_to_ferrum),
    ]