# Generated by Django 5.2.3 on 2025-07-07 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pipedata", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="area",
            name="geoloc",
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name="area",
            name="sector",
            field=models.CharField(max_length=250),
        ),
    ]
