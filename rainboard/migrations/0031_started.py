# Generated by Django 2.1.7 on 2019-03-06 23:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rainboard', '0030_remove_project_debug'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cibuild',
            options={'ordering': ('-started',)},
        ),
    ]
