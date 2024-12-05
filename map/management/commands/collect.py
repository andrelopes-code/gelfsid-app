from django.core.management.base import BaseCommand

from map.management.commands.collectors import charcoal_entries, suppliers_and_docs


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        suppliers_and_docs.collect()
        charcoal_entries.collect()

        self.stdout.write(self.style.SUCCESS('data collected successfully!'))
