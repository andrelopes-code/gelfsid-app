from django.core.management.base import BaseCommand

from map.management.collectors import charcoal_entries, suppliers_and_docs, suppliers_ratings


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        suppliers_and_docs.collect()
        # suppliers_ratings.collect()
        charcoal_entries.collect()

        self.stdout.write(self.style.SUCCESS('data collected successfully!'))
