# Generated by Django 2.0.5 on 2018-07-02 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rainboard", "0018_remove_target_python3"),
    ]

    operations = [
        migrations.AddField(
            model_name="target",
            name="active",
            field=models.BooleanField(default=True),
        ),
    ]
