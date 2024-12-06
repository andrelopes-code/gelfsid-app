from django.core.management.base import BaseCommand

from gelfmp.models import Supplier


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Supplier.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('database reset successfully!'))
