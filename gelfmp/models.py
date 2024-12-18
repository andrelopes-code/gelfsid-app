import os
from datetime import date

from django.db import models
from django.db.models.query import QuerySet
from django.forms import ValidationError

from gelfcore.logger import log
from gelfmp.services import geojson
from gelfmp.utils import dtutils, validators
from gelfmp.utils.normalization import normalize_text_upper, normalize_to_numbers

# ------------------ #
#  BASE MODEL CLASS  #
# ------------------ #


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        abstract = True


# ---------------------- #
#  TEXT CHOICES CLASSES  #
# ---------------------- #


class ContactType(models.TextChoices):
    WITNESS = 'witness', 'Testemunha'
    LEGAL_REPRESENTATIVE = 'legal_representative', 'Representante Legal'
    NEGOTIATION_RESP = 'accounting_responsible', 'Responsável do Setor Contábil'
    ACCOUNTING_RESP = 'negotiation_responsible', 'Responsável pela Negociação'
    NF_RESP = 'nf_responsible', 'Responsável pela Emissão de Notas Fiscais'
    LOGISTICS_RESP = 'logistics_responsible', 'Reponsável Programação e Logística'


class MonthType(models.IntegerChoices):
    JANUARY = 1, 'Janeiro'
    FEBRUARY = 2, 'Fevereiro'
    MARCH = 3, 'Março'
    APRIL = 4, 'Abril'
    MAY = 5, 'Maio'
    JUNE = 6, 'Junho'
    JULY = 7, 'Julho'
    AUGUST = 8, 'Agosto'
    SEPTEMBER = 9, 'Setembro'
    OCTOBER = 10, 'Outubro'
    NOVEMBER = 11, 'Novembro'
    DECEMBER = 12, 'Dezembro'


class MaterialType(models.TextChoices):
    IRON_ORE = 'Minério de Ferro', 'Minério de Ferro'
    BYPRODUCTS = 'Subprodutos', 'Subprodutos'
    CHARCOAL = 'Carvão Vegetal', 'Carvão Vegetal'
    BAUXITE = 'Bauxita', 'Bauxita'
    CLAY = 'Argila', 'Argila'
    SAND = 'Areia', 'Areia'
    LIMESTONE = 'Calcario', 'Calcario'
    FESIMG = 'FeSiMg', 'FeSiMg'
    FERROALLOYS = 'Ferroligas', 'Ferroligas'
    MIXTURE = 'Mistura', 'Mistura'
    FLUORITE = 'Fluorita', 'Fluorita'
    DOLOMITE = 'Dolomita', 'Dolomita'
    GRAPHITE = 'Grafite', 'Grafite'


class DocumentType(models.TextChoices):
    CTF = 'ctf', 'CADASTRO TÉCNICO FEDERAL'
    LIC_AMBIENTAL = 'lic_ambiental', 'LICENÇA AMBIENTAL'
    EXCEMPTION = 'exemption', 'DISPENSA'
    REGIEF = 'reg_ief', 'REGISTRO IEF'
    CAR = 'car', 'CADASTRO AMBIENTAL RURAL'
    STATE_REGISTRATION = 'state_registration', 'INSCRIÇÃO ESTADUAL'
    MUNICIPAL_REGISTRATION = 'municipal_registration', 'INSCRIÇÃO MUNICIPAL'
    CNPJ_LOOKUP = 'cnpj_lookup', 'CONSULTA CNPJ'
    SHAPEFILE = 'shapefile', 'SHAPEFILE'
    OTHER = 'other', 'OUTRO'


class SupplierType(models.TextChoices):
    GELF = 'gelf', 'GELF'
    BOTUMIRIM = 'botumirim', 'Botumirim'
    THIRD_PARTY = 'third_party', 'Terceiro'


def year_choices():
    current_year = date.today().year
    return [(year, str(year)) for year in range(current_year + 1, 2019, -1)]


# ----------- #
#  DB MODELS  #
# ----------- #


class State(models.Model):
    abbr = models.CharField(max_length=2, primary_key=True, verbose_name='Sigla')
    name = models.CharField(max_length=100, verbose_name='Nome')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')
    state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name='Estado')

    def __str__(self):
        return f'{self.name} - {self.state.abbr}'

    class Meta:
        ordering = ['name']
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'


class Contact(BaseModel):
    name = models.CharField(max_length=200, verbose_name='Nome')
    email = models.EmailField(verbose_name='Email')
    contact_type = models.CharField(max_length=50, choices=ContactType.choices, verbose_name='Função')

    primary_phone = models.CharField(max_length=20, verbose_name='Telefone Principal', null=True, blank=True)
    secondary_phone = models.CharField(max_length=20, verbose_name='Telefone Secundário', null=True, blank=True)

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name='Fornecedor',
    )

    def __str__(self):
        return f'{self.contact_type} - {self.name}'

    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'


class BankDetails(BaseModel):
    bank_name = models.CharField(max_length=255, verbose_name='Banco')
    agency = models.CharField(max_length=10, verbose_name='Agência')
    account_number = models.CharField(max_length=20, verbose_name='Número da Conta')

    bank_code = models.CharField(
        max_length=5,
        validators=[validators.validate_bank_code],
        verbose_name='Número do Banco',
    )

    def __str__(self):
        return f'{self.bank_name} - Cc: {self.account_number} Ag: {self.agency}'

    def save(self, *args, **kwargs):
        # Normaliza o nome do banco antes de salvar o registro.
        self.bank_name = normalize_text_upper(self.bank_name)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Detalhes Bancários'
        verbose_name_plural = 'Detalhes Bancários'
        ordering = ['bank_name']


class Document(BaseModel):
    def upload_to(instance, filename):
        return f'fornecedores/{instance.supplier.corporate_name}/documentos/{filename}'

    name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Nome de Exibição',
        help_text='Caso não informado, o nome do arquivo será usado para preencher este campo.',
    )

    file = models.FileField(
        upload_to=upload_to,
        max_length=255,
        verbose_name='Arquivo',
        validators=[validators.validate_max_file_size],
    )

    geojson = models.JSONField(
        blank=True,
        null=True,
        verbose_name='GeoJSON',
        help_text='Este campo é gerado automaticamente ao subir um Shapefile e não deve ser alterado manualmente.',
    )

    validity = models.DateField(
        blank=True,
        null=True,
        verbose_name='Validade',
        help_text=(
            'Caso não informado e o nome do arquivo contém a data, ela será usada para preencher este campo.\n'
            'Exemplo: nome do arquivo CTF_02.05.2020.pdf, a data 02/05/2020 será usada.'
        ),
    )

    document_type = models.CharField(max_length=50, choices=DocumentType.choices, verbose_name='Tipo de Documento')
    visible = models.BooleanField(default=True, verbose_name='Visível')

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Fornecedor',
    )

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    def delete(self, *args, **kwargs):
        try:
            # Remove o arquivo relacionado
            # ao registro de documento caso
            # seja encontrado.
            self.file.close()
            os.remove(self.file.path)

        except PermissionError as e:
            log.error(f'Erro ao tentar deletar arquivo de documento: {e}')
        except FileNotFoundError:
            pass

        super().delete(*args, **kwargs)

    def clean(self):
        # Caso não seja informado um nome de exibição
        # usar o próprio nome do arquivo.
        if not self.name:
            self.name = self.filename

        # Tenta extrair a data de validade do nome do
        # arquivo caso ela não seja informada.
        if (
            not self.validity
            and self.document_type != DocumentType.EXCEMPTION
            and self.document_type != DocumentType.OTHER
            and self.document_type != DocumentType.SHAPEFILE
        ):
            self.validity = dtutils.extract_date_from_text(self.filename)

        # Se o documento for um Shapefile obtem o GeoJSON
        # convertendo-o e armazenando no campo geojson.
        if self.document_type == DocumentType.SHAPEFILE:
            if self.file:
                try:
                    if self.file.name.lower().endswith('.zip'):
                        self.geojson = geojson.from_shapefile_zip(self.file)
                    else:
                        raise ValidationError('O arquivo enviado deve ser um arquivo ZIP válido.')

                except ValidationError as e:
                    raise e

        return super().clean()

    def save(self, *args, **kwargs):
        # Deleta o documento antigo se ao atualizar
        # seja um arquivo de mesmo nome.
        if self.pk:
            try:
                old_file = Document.objects.get(pk=self.pk).file

                if old_file and old_file.name != self.file.name:
                    if os.path.isfile(old_file.path):
                        os.remove(old_file.path)

            except Document.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.document_type} - {self.filename}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'


class CharcoalIQF(BaseModel):
    iqf = models.FloatField(verbose_name='IQF')

    planned_percentage = models.FloatField(
        validators=[validators.validate_percentage], verbose_name='Programação Realizada (%)'
    )

    fines_percentage = models.FloatField(validators=[validators.validate_percentage], verbose_name='Finos (%)')
    moisture_percentage = models.FloatField(validators=[validators.validate_percentage], verbose_name='Umidade (%)')
    density_percentage = models.FloatField(validators=[validators.validate_percentage], verbose_name='Densidade (%)')

    month = models.IntegerField(choices=MonthType.choices, verbose_name='Mês')
    year = models.IntegerField(choices=year_choices(), verbose_name='Ano')

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='iqfs',
        verbose_name='Fornecedor',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['supplier', 'month', 'year'],
                name='charcoal_iqf_supplier_month_year_unique_constraint',
            )
        ]
        verbose_name = 'IQF de Fornecedor de Carvão'
        verbose_name_plural = 'IQFs de Fornecedores de Carvão'


class CharcoalMonthlyPlan(BaseModel):
    planned_volume = models.FloatField(verbose_name='Volume Programado (m³)')
    month = models.IntegerField(choices=MonthType.choices, verbose_name='Mês')
    year = models.IntegerField(choices=year_choices(), verbose_name='Ano')

    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Preço (R$)',
        help_text='Somente aplicável a GELF.',
    )

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='monthly_plans',
        verbose_name='Fornecedor',
    )

    def clean(self):
        # Validação do campo 'price' com base no nome do fornecedor,
        # o campo preço é aplicável apenas a própria GELF.
        if self.price is not None and 'GELF' not in self.supplier.corporate_name.upper():
            raise ValidationError({'price': 'O campo `Preço` não é aplicavel a esse fornecedor.'})

        return super().clean()

    def __str__(self):
        return f'{self.supplier} - {self.month}/{self.year}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['supplier', 'month', 'year'],
                name='charcoal_monthly_plan_supplier_month_year_unique_constraint',
            )
        ]
        verbose_name = 'Programação de Carvão'
        verbose_name_plural = 'Programações de Carvão'


class CharcoalEntry(BaseModel):
    origin_ticket = models.CharField(max_length=50, unique=True, verbose_name='Ticket de Origem')
    vehicle_plate = models.CharField(max_length=50, verbose_name='Placa do Veículo')
    origin_volume = models.FloatField(verbose_name='Volume de Origem (m³)')
    entry_volume = models.FloatField(verbose_name='Volume de Entrada (m³)')
    entry_date = models.DateField(verbose_name='Data de Entrada')
    moisture = models.FloatField(verbose_name='Umidade (%)')
    fines = models.FloatField(verbose_name='Finos (%)')
    density = models.FloatField(verbose_name='Densidade')

    dcf = models.CharField(max_length=50, validators=[validators.validate_dcf], verbose_name='DCF')
    gcae = models.CharField(max_length=50, verbose_name='GCAE')

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='charcoal_entries',
        verbose_name='Fornecedor',
    )

    def __str__(self):
        return f'{self.entry_volume} - {self.entry_date} - {self.supplier}'

    class Meta:
        ordering = ['-entry_date']
        indexes = [
            models.Index(fields=['entry_date']),
            models.Index(fields=['supplier']),
            models.Index(fields=['dcf']),
        ]
        verbose_name = 'Entrada de Carvão'
        verbose_name_plural = 'Entradas de Carvão'


class Supplier(BaseModel):
    corporate_name = models.CharField(
        max_length=200,
        verbose_name='Razão Social',
        unique=True,
        help_text='Insira nomes padronizados para evitar inconsistência, como o próprio nome que consta no CNPJ.',
    )

    rm_code = models.CharField(max_length=30, null=True, blank=True, unique=True, verbose_name='Código RM')
    active = models.BooleanField(default=True, verbose_name='Fornecedor Ativo')

    material_type = models.CharField(max_length=100, choices=MaterialType.choices, verbose_name='Tipo de Material')
    supplier_type = models.CharField(
        max_length=100, choices=SupplierType.choices, null=True, blank=True, verbose_name='Tipo de Fornecedor'
    )

    distance_in_meters = models.IntegerField(blank=True, null=True, verbose_name='Distância em Metros')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Endereço')
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='suppliers', verbose_name='Estado')
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='suppliers', verbose_name='Cidade')

    cep = models.CharField(
        max_length=10,
        validators=[validators.validate_cep],
        verbose_name='CEP',
    )

    latitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        validators=[validators.validate_latitude],
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        validators=[validators.validate_longitude],
        null=True,
        blank=True,
    )

    state_registration = models.CharField(max_length=50, verbose_name='Inscrição Estadual', null=True, blank=True)
    municipal_registration = models.CharField(max_length=50, verbose_name='Inscrição Municipal', null=True, blank=True)
    xml_email = models.EmailField(verbose_name='Email XML', null=True, blank=True)

    cpf_cnpj = models.CharField(
        unique=True,
        max_length=18,
        validators=[validators.validate_cpf_cnpj],
        verbose_name='CPF ou CNPJ',
    )

    observations = models.TextField(
        max_length=2000,
        blank=True,
        null=True,
        verbose_name='Observações',
        help_text='Adicione informações adicionais ou observações relevantes.',
    )

    bank_details = models.OneToOneField(
        BankDetails,
        on_delete=models.SET_NULL,
        verbose_name='Detalhes Bancários',
        null=True,
        blank=True,
    )

    def get_visible_documents(self) -> QuerySet[Document]:
        return self.documents.filter(visible=True)

    def get_iqfs(self) -> models.Manager[CharcoalIQF]:
        return self.iqfs

    def save(self, *args, **kwargs):
        # Normaliza os campos para evitar inconsistência nos dados.
        self.corporate_name = normalize_text_upper(self.corporate_name)
        self.cpf_cnpj = normalize_to_numbers(self.cpf_cnpj)
        self.address = normalize_text_upper(self.address)
        self.cep = normalize_to_numbers(self.cep)

        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Deleta detalhes de banco relacionados
        # ao fornecedor caso exista algum.
        if self.bank_details:
            self.bank_details.delete()

        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['corporate_name']

        indexes = [
            models.Index(fields=['material_type']),
            models.Index(fields=['state']),
            models.Index(fields=['cpf_cnpj']),
        ]

        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'

    def __str__(self):
        return self.corporate_name
