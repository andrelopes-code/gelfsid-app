from django.core.management.base import BaseCommand

from gelfmp.models import City, MaterialType, State, Supplier


def load(cmd: BaseCommand):
    try:
        gelf = Supplier.objects.get(id=1)
        cmd.stdout.write(cmd.style.SUCCESS(f'O fornecedor {gelf.corporate_name} já existe.'))

    except Supplier.DoesNotExist:
        gelf = Supplier.objects.create(
            id=1,
            corporate_name='GELF SIDERURGIA S/A FAZENDA TAMANDUA_POCOES',
            material_type=MaterialType.CHARCOAL,
            cep=35701970,
            cpf_cnpj='20388757000101',
            state=State.objects.filter(abbr='MG').get(),
            city=City.objects.filter(name='Sete Lagoas', state__abbr='MG').get(),
        )
        cmd.stdout.write(cmd.style.SUCCESS(f'O fornecedor {gelf.corporate_name} foi criado.'))
