# Generated by Django 2.2.8 on 2019-12-12 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rainboard', '0039_end_trusty'),
    ]

    operations = [
        migrations.AddField(
            model_name='robotpkg',
            name='same_py',
            field=models.BooleanField(default=True),
        ),
    ]