from time import sleep
from django.core.management.base import BaseCommand
from gelfsid.logger import logger
from map.models import FornecedorMateriaPrima
from map.utils.distance_calculator import DistanceCalculator


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        fornecedores = FornecedorMateriaPrima.objects.all()

        for fornecedor in fornecedores:
            if fornecedor.distancia_em_metros:
                continue

            try:
                sleep(0.1)
                route_info = DistanceCalculator.get_distance(
                    f'{fornecedor.cidade.nome}, {fornecedor.cidade.estado}', 'Sete Lagoas MG', fetch_new=True
                )
                print(route_info)

            except Exception as e:
                logger.error(e)
                continue

            fornecedor.distancia_em_metros = route_info.distance_in_meters
            fornecedor.save()
