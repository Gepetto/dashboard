# Generated by Django 2.1.4 on 2019-01-16 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rainboard", "0026_archived"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="suffix",
            field=models.CharField(default="", max_length=50),
        ),
    ]
