# Generated by Django 5.0 on 2024-01-21 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tsd_main_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='is_patient_viewed',
            field=models.BooleanField(default=False),
        ),
    ]
