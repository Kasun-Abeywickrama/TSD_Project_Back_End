# Generated by Django 5.0 on 2023-12-30 00:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tsd_main_app', '0009_rename_admindetails_admin'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_date', models.DateField(auto_now_add=True)),
                ('scheduled_date', models.DateField(null=True)),
                ('scheduled_time_period', models.CharField(max_length=100, null=True)),
                ('response_description', models.CharField(max_length=1000, null=True)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tsd_main_app.admin')),
                ('quiz_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tsd_main_app.quizresult')),
            ],
        ),
        migrations.AddField(
            model_name='admin',
            name='quiz_result',
            field=models.ManyToManyField(through='tsd_main_app.Appointment', to='tsd_main_app.quizresult'),
        ),
    ]
