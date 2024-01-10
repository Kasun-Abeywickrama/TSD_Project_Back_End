# Generated by Django 5.0 on 2024-01-07 04:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tsd_main_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=1000)),
                ('image', models.CharField(max_length=200)),
                ('fe_route', models.CharField(max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='email',
        ),
        migrations.AddField(
            model_name='authuser',
            name='age',
            field=models.IntegerField(null=True),
        ),
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
        migrations.AddField(
            model_name='quizresult',
            name='is_seen',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='quizresult',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='mobile_number',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, null=True)),
                ('last_name', models.CharField(max_length=50, null=True)),
                ('mobile_number', models.CharField(max_length=50, null=True)),
                ('location', models.CharField(max_length=200, null=True)),
                ('website', models.CharField(max_length=200, null=True)),
                ('auth_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_date', models.DateField(auto_now_add=True)),
                ('is_checked', models.BooleanField()),
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
        migrations.AddField(
            model_name='authuser',
            name='role',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tsd_main_app.role'),
        ),
        migrations.CreateModel(
            name='RolePage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create', models.BooleanField(default=False)),
                ('read', models.BooleanField(default=False)),
                ('update', models.BooleanField(default=False)),
                ('delete', models.BooleanField(default=False)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tsd_main_app.page')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tsd_main_app.role')),
            ],
        ),
        migrations.AddField(
            model_name='role',
            name='pages',
            field=models.ManyToManyField(through='tsd_main_app.RolePage', to='tsd_main_app.page'),
        ),
    ]
