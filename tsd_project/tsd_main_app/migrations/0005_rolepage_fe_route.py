# Generated by Django 5.0 on 2023-12-28 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tsd_main_app', '0004_remove_page_permission_remove_role_permission_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rolepage',
            name='fe_route',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
