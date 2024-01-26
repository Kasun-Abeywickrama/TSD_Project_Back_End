# Generated by Django 5.0 on 2024-01-26 20:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tsd_main_app', '0003_admin_profile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivateQuestions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('private_question', models.CharField(max_length=500)),
                ('private_answer', models.CharField(max_length=500)),
                ('asked_date', models.DateField(auto_now_add=True)),
                ('asked_time', models.TimeField(auto_now_add=True)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tsd_main_app.admin')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tsd_main_app.patient')),
            ],
        ),
        migrations.AddField(
            model_name='admin',
            name='patient',
            field=models.ManyToManyField(through='tsd_main_app.PrivateQuestions', to='tsd_main_app.patient'),
        ),
    ]