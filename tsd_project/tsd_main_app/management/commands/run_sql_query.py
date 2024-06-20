from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Run custom SQL queries after migrations'

    def handle(self, *args, **kwargs):
        sql_statements = [
            """
            INSERT INTO tsd_main_app_page (id, title, description, image, fe_route) VALUES 
            (1, 'Accounts', 'Accounts Page', 'asd', 'accounts/'),
            (2, 'Roles', 'Roles Page', 'asd', 'roles/'),
            (3, 'Quiz', 'Quiz Page', 'qwe', 'question_select/'),
            (4, 'Quiz Result', 'Quiz result Page', 'asd', 'quiz-result-list/'),
            (5, 'Appointments', 'Appointments Page', 'asdf', 'appointment-list/'),
            (6, 'Private Questions', 'Questions Page', 'asd', 'private-questions/');
            """,
            """
            INSERT INTO tsd_main_app_role (id, name) VALUES 
            (1, 'Admin'),
            (2, 'Co-Admin'),
            (3, 'Counselor'),
            (4, 'Patient');
            """,
            """
            INSERT INTO tsd_main_app_authuser (id, username, password, is_superuser, first_name, last_name, email, is_staff, is_active, date_joined, auth_user_type, role_id) VALUES 
            (1, 'main_admin', 'pbkdf2_sha256$720000$olTEQEl886PlKfymbfLqU9$eyp7vxyym16KcwUH8wXPpwcSatgJEswuevmb3uD5Uz8=', 1, 'Main', 'Admin', 'admin@example.com', 1, 1, '2024-06-20 07:00:00.000000', 'admin', 1);
            """,
            """
            INSERT INTO tsd_main_app_rolepage (id, can_create, can_read, can_update, can_delete, page_id, role_id) VALUES 
            (1, 1, 1, 1, 1, 1, 1),
            (2, 1, 1, 1, 1, 2, 1),
            (3, 1, 1, 1, 1, 3, 1),
            (4, 1, 1, 1, 1, 4, 1),
            (5, 1, 1, 1, 1, 5, 1),
            (6, 1, 1, 1, 1, 6, 1);
            """
        ]
        
        with connection.cursor() as cursor:
            for statement in sql_statements:
                cursor.execute(statement)
        
        self.stdout.write(self.style.SUCCESS('Successfully executed the SQL queries'))
