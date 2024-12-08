from django.core.management.base import BaseCommand

from gelfcore.logger import log
from gelfmp.services.iqf_calculator import calculate_suppliers_iqf


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-m', type=int, help='Mês para o cálculo do IQF (1-12)', required=True)
        parser.add_argument('-y', type=int, help='Ano para o cálculo do IQF', required=True)

    def handle(self, *args, **kwargs):
        month = kwargs['m']
        year = kwargs['y']

        try:
            calculate_suppliers_iqf(month, year)
        except Exception as e:
            log.error(f'Erro inesperado durante o cálculo do IQF: {e}')
