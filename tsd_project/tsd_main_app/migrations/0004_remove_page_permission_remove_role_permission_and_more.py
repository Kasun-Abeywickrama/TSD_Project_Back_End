# Generated by Django 5.0 on 2023-12-28 08:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tsd_main_app', '0003_permission_admin_page_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='permission',
        ),
        migrations.RemoveField(
            model_name='role',
            name='permission',
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
        migrations.DeleteModel(
            name='Permission',
        ),
    ]