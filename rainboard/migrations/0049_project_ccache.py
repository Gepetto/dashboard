# Generated by Django 3.0.9 on 2020-08-05 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rainboard', '0048_namespace_from_gepetto'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='ccache',
            field=models.BooleanField(default=True),
        ),
    ]
