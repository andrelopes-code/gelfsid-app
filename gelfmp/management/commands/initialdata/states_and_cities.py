import json

from django.conf import settings
from django.core.management.base import BaseCommand

from gelfmp.models import City, State


def load(cmd: BaseCommand):
    with open(settings.STATES_AND_CITIES_PATH, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for state, cities in data.items():
        db_state, _ = State.objects.get_or_create(abbr=state, name=state)

        for city in cities:
            City.objects.get_or_create(name=city, state=db_state)
            cmd.stdout.write(cmd.style.SUCCESS(f'created: {city} - {state}'))

    cmd.stdout.write(cmd.style.SUCCESS('states and cities loaded successfully!'))
