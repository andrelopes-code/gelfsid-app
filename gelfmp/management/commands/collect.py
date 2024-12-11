from django.core.management.base import BaseCommand

from gelfmp.management.commands.collectors import charcoal_entries, charcoal_schedule, suppliers_and_docs


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        suppliers_and_docs.collect()
        charcoal_entries.collect()
        charcoal_schedule.collect()

        self.stdout.write(self.style.SUCCESS('data collected successfully!'))
