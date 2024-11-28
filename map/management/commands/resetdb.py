from django.core.management.base import BaseCommand

from map.models import Document, Supplier


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Supplier.objects.all().delete()
        Document.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('database reset successfully!'))
