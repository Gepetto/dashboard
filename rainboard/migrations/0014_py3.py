# Generated by Django 2.0.5 on 2018-05-16 14:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0013_target_python3"),
    ]

    operations = [
        migrations.AddField(
            model_name="image",
            name="py3",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name="image",
            unique_together={("robotpkg", "target", "py3")},
        ),
    ]
