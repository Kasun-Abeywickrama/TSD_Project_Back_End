# Generated by Django 5.0 on 2024-06-18 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tsd_main_app', '0005_privatequestions_is_checked'),
    ]

    operations = [
        migrations.AddField(
            model_name='privatequestions',
            name='is_patient_viewed',
            field=models.BooleanField(default=True),
        ),
    ]
