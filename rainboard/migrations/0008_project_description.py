# Generated by Django 2.0.1 on 2018-01-30 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rainboard', '0007_auto_20180130_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='description',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
