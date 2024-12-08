from django.core.management.base import BaseCommand

from gelfmp.models import Supplier
from gelfmp.services.distance_calculator import DistanceCalculator


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        fornecedores = Supplier.objects.all()

        for fornecedor in fornecedores:
            if fornecedor.distance_in_meters:
                continue

            try:
                target = f'{fornecedor.city.name}, {fornecedor.city.state}'
                route_info = DistanceCalculator.get_distance(target, 'Sete Lagoas MG', fetch_new=True)
                self.stdout.write(self.style.SUCCESS(f'Fornecedor: {fornecedor.corporate_name}'))

            except Exception as e:
                self.stderr.write(self.style.ERROR(e))
                continue

            fornecedor.distance_in_meters = route_info.distance_in_meters

            fornecedor.save()
