from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.core.management import call_command

class TsdMainAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tsd_main_app'

    def ready(self):
        post_migrate.connect(run_custom_sql, sender=self)

def run_custom_sql(sender, **kwargs):
    call_command('run_sql_query')