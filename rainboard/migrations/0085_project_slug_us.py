# Generated by Django 5.0.6 on 2024-10-07 16:24

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rainboard", "0084_add_noble"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="slug_us",
            field=autoslug.fields.AutoSlugField(
                default="",
                editable=False,
                populate_from="slug",
                unique=False,
            ),
            preserve_default=False,
        ),
    ]
