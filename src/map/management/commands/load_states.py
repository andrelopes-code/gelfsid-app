import json

from django.core.management.base import BaseCommand

from gelfsid.settings import settings

from ...models import City, State


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open(settings.CITIES_STATES_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for state, cities in data.items():
            db_state, _ = State.objects.get_or_create(abbr=state, name=state)

            for city in cities:
                City.objects.get_or_create(name=city, state=db_state)
                self.stdout.write(self.style.SUCCESS(f'created: {city} - {state}'))

        self.stdout.write(self.style.SUCCESS('states and cities loaded successfully!'))
