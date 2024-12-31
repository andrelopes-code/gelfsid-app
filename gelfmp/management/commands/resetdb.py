from django.core.management.base import BaseCommand

from gelfmp import models


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        models.DCF().all().delete()
        models.CharcoalContract().all().delete()
        models.CharcoalEntry().all().delete()
        models.Document.objects.all().delete()
        models.Supplier.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('database reset successfully!'))
