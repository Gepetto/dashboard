# Generated by Django 2.2.9 on 2020-01-17 17:34

from django.db import migrations, models


def main_bionic(apps, schema_editor):
    Target = apps.get_model('rainboard', 'Target')
    Target.objects.filter(name='18.04').update(main=True)



class Migration(migrations.Migration):

    dependencies = [
        ('rainboard', '0040_robotpkg_same_py'),
    ]

    operations = [
        migrations.AddField(
            model_name='target',
            name='main',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(main_bionic),
    ]
