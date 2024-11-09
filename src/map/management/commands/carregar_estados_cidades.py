from django.core.management.base import BaseCommand
import json
from ...models import Estado, Cidade


class Command(BaseCommand):
    help = 'Carrega estados e cidades do arquivo JSON'

    def handle(self, *args, **kwargs):
        with open('static/data/states_cities.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        for e, c in data.items():
            estado, _ = Estado.objects.get_or_create(sigla=e, nome=e)
            for cidade_nome in c:
                Cidade.objects.get_or_create(nome=cidade_nome, estado=estado)

        self.stdout.write(
            self.style.SUCCESS('Estados e cidades carregados com sucesso!')
        )
