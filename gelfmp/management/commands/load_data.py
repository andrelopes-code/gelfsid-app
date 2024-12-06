from django.core.management.base import BaseCommand

from gelfmp.management.commands.initialdata import states_and_cities


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        states_and_cities.load(self)
