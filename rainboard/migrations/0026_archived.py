# Generated by Django 2.1.3 on 2019-01-10 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rainboard', '0025_auto_20181217_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='repo',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]