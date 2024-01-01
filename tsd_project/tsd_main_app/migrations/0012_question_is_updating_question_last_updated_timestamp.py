# Generated by Django 5.0 on 2023-12-31 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tsd_main_app', '0011_appointment_accepted'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='is_updating',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='question',
            name='last_updated_timestamp',
            field=models.DateTimeField(null=True),
        ),
    ]
