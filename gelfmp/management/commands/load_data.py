from django.core.management import call_command
from django.core.management.base import BaseCommand

from gelfmp.management.commands.initialdata import gelf_supplier_data


def load_fixtures(cmd: BaseCommand):
    try:
        call_command('loaddata', 'state_fixture.json')
        call_command('loaddata', 'city_fixture.json')
        call_command('loaddata', 'admin_interface_theme_gelf.json')
        cmd.stdout.write(cmd.style.SUCCESS("Fixtures carregadas com sucesso."))
    except Exception as e:
        cmd.stderr.write(cmd.style.ERROR(f"Erro ao carregar fixtures: {e}"))


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        load_fixtures(self)
        gelf_supplier_data.load(self)
