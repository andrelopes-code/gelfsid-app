import pandas as pd
from django.core.management.base import BaseCommand

from map.models import CharcoalEntry


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        entries = CharcoalEntry.objects.all().values('supplier__corporate_name', 'entry_volume')
        df = pd.DataFrame(entries)
        df = df.groupby('supplier__corporate_name')

        self.stdout.write(self.style.SUCCESS('database reset successfully!'))
