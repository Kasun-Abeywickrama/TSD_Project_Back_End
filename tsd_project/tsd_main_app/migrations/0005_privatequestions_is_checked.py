# Generated by Django 5.0 on 2024-06-18 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tsd_main_app', '0004_privatequestions_admin_patient'),
    ]

    operations = [
        migrations.AddField(
            model_name='privatequestions',
            name='is_checked',
            field=models.BooleanField(default=False),
        ),
    ]