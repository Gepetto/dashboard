# Generated by Django 2.0.2 on 2018-02-16 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rainboard', '0004_contributor_contributormail_contributorname'),
    ]

    operations = [
        migrations.AddField(
            model_name='contributor',
            name='agreement_signed',
            field=models.BooleanField(default=False),
        ),
    ]