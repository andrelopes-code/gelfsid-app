from ...models import (
    FornecedorMateriaPrima,
    RegistroIEF,
    CadastroTecnicoFederal,
    LicencaAmbiental,
)
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        LicencaAmbiental.objects.all().delete()
        CadastroTecnicoFederal.objects.all().delete()
        RegistroIEF.objects.all().delete()
        FornecedorMateriaPrima.objects.all().delete()
