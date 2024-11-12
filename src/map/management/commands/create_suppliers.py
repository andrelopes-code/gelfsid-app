import random
from django.core.management.base import BaseCommand
from faker import Faker
from ...models import FornecedorMateriaPrima, Estado, Cidade
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

fake = Faker('pt_BR')


class Command(BaseCommand):
    help = 'Gera fornecedores aleatórios para cidades do estado MG'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Número de fornecedores a serem criados')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        self.stdout.write(f'Gerando {count} fornecedores...')

        try:
            # Buscar o estado "MG" no banco de dados
            estado_mg = Estado.objects.get(sigla='MG')
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR('Estado "MG" não encontrado no banco de dados.'))
            return

        # Buscar todas as cidades do estado "MG"
        cidades_mg = Cidade.objects.filter(estado=estado_mg)

        if not cidades_mg.exists():
            self.stdout.write(self.style.ERROR('Nenhuma cidade encontrada para o estado "MG".'))
            return

        for _ in range(count):
            # Gerar dados aleatórios para o fornecedor
            razao_social = fake.company()
            cnpj = fake.cnpj().replace('.', '').replace('/', '').replace('-', '')
            tipo_material = random.choice(['CAR', 'MIN'])
            licenca = fake.bothify(text='LA-2024-#####')
            registro_ief = fake.bothify(text=' IEF-REG-######')
            cadastro_tecnico_federal = fake.bothify(text='CTF-APP-######')
            nota_qualidade = round(random.uniform(0, 100), 1)
            cidade = random.choice(cidades_mg)

            try:
                # Criar a instância do fornecedor
                fornecedor = FornecedorMateriaPrima.objects.create(
                    razao_social=razao_social,
                    cnpj=cnpj,
                    tipo_material=tipo_material,
                    licenca=licenca,
                    registro_ief=registro_ief,
                    cadastro_tecnico_federal=cadastro_tecnico_federal,
                    nota_qualidade=nota_qualidade,
                    estado=estado_mg,
                    cidade=cidade,
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Fornecedor criado: {fornecedor.razao_social} - {fornecedor.cpf_cnpj}')
                )
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f'Erro ao criar fornecedor: {e}'))

        self.stdout.write(self.style.SUCCESS(f'{count} fornecedores gerados com sucesso!'))
