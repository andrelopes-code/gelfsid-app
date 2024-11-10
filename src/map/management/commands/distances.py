from time import sleep
from django.core.management.base import BaseCommand
from map.models import FornecedorMateriaPrima
from map.utils.distance_calculator import DistanceCalculator


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        fornecedores = FornecedorMateriaPrima.objects.all()

        for fornecedor in fornecedores:
            sleep(0.5)
            route_info = DistanceCalculator.get_distance(
                f'{fornecedor.cidade.nome}, {fornecedor.cidade.estado}', 'Sete Lagoas MG', fetch_new=True
            )

            print(f'{fornecedor.razao_social}: {route_info.distance_in_meters / 1000:.1f} km')
