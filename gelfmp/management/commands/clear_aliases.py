import os

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        aliases_files = [
            os.path.join(path, file)
            for path, _, files in os.walk(settings.BASE_DIR)
            for file in files
            if file.endswith('.alias.json')
        ]

        for alias_file in aliases_files:
            print('Tem certeza que deseja remover:\n')
            print(f'  {alias_file}')

            if input('\n[y/N] ? ') == 'y':
                os.remove(alias_file)
