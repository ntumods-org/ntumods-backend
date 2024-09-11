from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings
from django.db import connection


'''
Usage: python manage.py reset_db
This command deletes all data from the database and resets the primary key sequence.
Use with caution as this action is irreversible.
'''
class Command(BaseCommand):
    help = 'Deletes all data from the database and resets the primary key sequence'

    def handle(self, *args, **kwargs):
        # confirmation prompt
        self.stdout.write(self.style.WARNING('YOU ARE ABOUT TO DELETE ALL DATA FROM THE DATABASE, THIS ACTION IS IRREVERSIBLE!!! ARE YOU SURE YOU WANT TO PROCEED?'))
        confirmation = input(self.style.NOTICE('Type \'CONFIRM DELETE\' to proceed: '))
        if confirmation != 'CONFIRM DELETE':
            self.stdout.write(self.style.ERROR('Delete operation cancelled'))
            return

        # delete all data from all tables
        all_models = apps.get_models()
        for model in all_models:
            model.objects.all().delete()

        # reset primary key sequences
        with connection.cursor() as cursor:
            if 'sqlite' not in settings.DATABASES['default']['ENGINE']:
                for model in all_models:
                    table_name = model._meta.db_table
                    cursor.execute(f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1;")
            else:
                cursor.execute("DELETE FROM sqlite_sequence;")
            
        self.stdout.write(self.style.SUCCESS('Successfully deleted all data from the database and reset primary key sequences'))
