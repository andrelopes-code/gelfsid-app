from django.core.management import call_command
from django.core.management.base import BaseCommand


def load_fixtures(cmd: BaseCommand):
    try:
        call_command('loaddata', 'states.json')
        call_command('loaddata', 'cities.json')
        call_command('loaddata', 'admin_interface_theme_gelf.json')
        call_command('loaddata', 'gelf_supplier_data.json')
        cmd.stdout.write(cmd.style.SUCCESS('Fixtures carregadas com sucesso.'))
    except Exception as e:
        cmd.stderr.write(cmd.style.ERROR(f'Erro ao carregar fixtures: {e}'))


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        load_fixtures(self)
