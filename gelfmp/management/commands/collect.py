from django.core.management.base import BaseCommand

from gelfmp.management.commands.collectors import charcoal_entries


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # suppliers_and_docs.collect()
        charcoal_entries.collect()

        self.stdout.write(self.style.SUCCESS('data collected successfully!'))
