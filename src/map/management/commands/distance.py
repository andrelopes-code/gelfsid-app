from django.core.management.base import BaseCommand
from map.utils.distance_calculator import DistanceCalculator


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print(DistanceCalculator.get_distance('Sete Lagoas MG', 'Belo Horizonte MG'))
