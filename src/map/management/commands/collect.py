from django.core.management.base import BaseCommand

from .collect_excel_data import collect


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        collect.run()

        self.stdout.write(self.style.SUCCESS('data collected successfully!'))
