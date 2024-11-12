from .collect_excel import collect_data
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        collect_data.run()
