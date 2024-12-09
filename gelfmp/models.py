from datetime import date

from django.db import models
from django.db.models.query import QuerySet

from gelfmp.utils import validators
from gelfmp.utils.normalization import normalize_text_upper

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
    contact_type = models.CharField(max_length=50, choices=ContactType.choices, verbose_name='Função')
    name = models.CharField(max_length=200, verbose_name='Nome')
    email = models.EmailField(verbose_name='Email')
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
    bank_code = models.CharField(
        max_length=5,
        validators=[validators.validate_bank_code],
        verbose_name='Número do Banco',
    )
    bank_name = models.CharField(max_length=255, verbose_name='Banco')
    agency = models.CharField(max_length=10, verbose_name='Agência')
    account_number = models.CharField(max_length=20, verbose_name='Número da Conta')

    def __str__(self):
        return f'{self.bank_name} - {self.account_number} ({self.agency})'

    def save(self, *args, **kwargs):
        self.bank_name = normalize_text_upper(self.bank_name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Detalhes Bancários'
        verbose_name_plural = 'Detalhes Bancários'
        ordering = ['bank_name']


class Document(BaseModel):
    name = models.CharField(max_length=80, verbose_name='Nome')
    type = models.CharField(max_length=80, verbose_name='Tipo de Documento')
    filepath = models.CharField(max_length=355, blank=True, null=True, verbose_name='Link do Arquivo')
    validity = models.DateField(blank=True, null=True, verbose_name='Validade')

    def save(self, *args, **kwargs):
        self.name = normalize_text_upper(self.name)
        self.type = self.type.upper()
        super().save(*args, **kwargs)

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Fornecedor',
    )

    def __str__(self):
        return f'{self.type} - {self.name}'

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'


class CharcoalIQF(BaseModel):
    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='iqfs',
        verbose_name='Fornecedor',
    )

    iqf = models.FloatField(verbose_name='IQF')
    programmed_percentage = models.FloatField(
        validators=[validators.validate_percentage], verbose_name='Programação Realizada (%)'
    )
    fines_percentage = models.FloatField(validators=[validators.validate_percentage], verbose_name='Finos (%)')
    moisture_percentage = models.FloatField(validators=[validators.validate_percentage], verbose_name='Umidade (%)')
    density_percentage = models.FloatField(validators=[validators.validate_percentage], verbose_name='Densidade (%)')

    month = models.IntegerField(choices=MonthType.choices, verbose_name='Mês')
    year = models.IntegerField(choices=year_choices(), verbose_name='Ano')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['supplier', 'month', 'year'],
                name='charcoal_iqf_supplier_month_year_unique_constraint',
            )
        ]
        verbose_name = 'IQF de Fornecedor de Carvão'
        verbose_name_plural = 'IQFs de Fornecedores de Carvão'


class CharcoalMonthlyPlan(models.Model):
    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='monthly_plans',
        verbose_name='Fornecedor',
    )
    month = models.IntegerField(choices=MonthType.choices, verbose_name='Mês')
    year = models.IntegerField(choices=year_choices(), verbose_name='Ano')
    programmed_volume = models.FloatField(verbose_name='Volume Programado (m³)')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['supplier', 'month', 'year'],
                name='charcoal_monthly_plan_supplier_month_year_unique_constraint',
            )
        ]
        verbose_name = 'Programação de Carvão'
        verbose_name_plural = 'Programações de Carvão'

    def __str__(self):
        return f'{self.supplier} - {self.month}/{self.year}'


class CharcoalEntry(BaseModel):
    entry_date = models.DateField(verbose_name='Data de Entrada')
    origin_ticket = models.CharField(max_length=50, unique=True, verbose_name='Ticket de Origem')
    vehicle_plate = models.CharField(max_length=50, verbose_name='Placa do Veículo')
    origin_volume = models.FloatField(verbose_name='Volume de Origem (m³)')
    entry_volume = models.FloatField(verbose_name='Volume de Entrada (m³)')
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
        indexes = [models.Index(fields=['entry_date'])]
        verbose_name = 'Entrada de Carvão'
        verbose_name_plural = 'Entradas de Carvão'


class Supplier(BaseModel):
    rm_code = models.CharField(max_length=30, null=True, blank=True, unique=True, verbose_name='Código RM')
    active = models.BooleanField(default=True, verbose_name='Fornecedor Ativo')
    corporate_name = models.CharField(
        max_length=200,
        verbose_name='Razão Social',
        unique=True,
        help_text='Insira nomes padronizados para evitar inconsistência, como o próprio nome que consta no CNPJ.',
    )

    material_type = models.CharField(max_length=100, choices=MaterialType.choices, verbose_name='Tipo de Material')

    distance_in_meters = models.IntegerField(blank=True, null=True, verbose_name='Distância em Metros')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Endereço')
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='suppliers', verbose_name='Estado')
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='suppliers', verbose_name='Cidade')
    cep = models.CharField(
        max_length=8,
        validators=[validators.validate_cep],
        help_text='Insira apenas os números.',
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
        max_length=14,
        validators=[validators.validate_cpf_cnpj],
        verbose_name='CPF ou CNPJ',
        help_text='Insira apenas os números.',
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

    def get_documents(self) -> QuerySet[Document]:
        return self.documents.all()

    def get_contacts(self) -> QuerySet[Contact]:
        return self.contacts.all()

    def get_iqfs(self) -> models.Manager[CharcoalIQF]:
        return self.iqfs

    def save(self, *args, **kwargs):
        self.corporate_name = normalize_text_upper(self.corporate_name)
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.bank_details:
            self.bank_details.delete()

        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['corporate_name']

        indexes = [
            models.Index(fields=['material_type']),
            models.Index(fields=['state']),
        ]

        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'

    def __str__(self):
        return self.corporate_name
