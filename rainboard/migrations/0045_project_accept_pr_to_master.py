# Generated by Django 3.0.8 on 2020-07-24 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rainboard", "0044_focal"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="accept_pr_to_master",
            field=models.BooleanField(default=False),
        ),
    ]
