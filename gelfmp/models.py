from django.db import models

from gelfmp.validators import custom_validators as cv

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
    NF_RESP = 'nf_resp', 'Responsável pela Emissão de Notas Fiscais'


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

    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'


class BankDetails(models.Model):
    bank_code = models.CharField(max_length=4, verbose_name='Número do Banco')
    bank_name = models.CharField(max_length=255, verbose_name='Banco')
    agency = models.CharField(max_length=10, verbose_name='Agência')
    account_number = models.CharField(max_length=20, verbose_name='Número da Conta')

    def __str__(self):
        return f'{self.bank_name} - {self.account_number} ({self.agency})'

    class Meta:
        verbose_name = 'Detalhes Bancários'
        verbose_name_plural = 'Detalhes Bancários'
        ordering = ['bank_name']


class Document(BaseModel):
    name = models.CharField(max_length=80, verbose_name='Nome')
    type = models.CharField(max_length=80, verbose_name='Tipo de Documento')
    filepath = models.CharField(max_length=355, blank=True, null=True, verbose_name='Link do Arquivo')
    validity = models.DateField(blank=True, null=True, verbose_name='Validade')

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Fornecedor',
    )

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'


class CharcoalEntry(BaseModel):
    entry_date = models.DateField(verbose_name='Data de Entrada')
    origin_ticket = models.CharField(max_length=50, unique=True, verbose_name='Ticket de Origem')
    vehicle_plate = models.CharField(max_length=50, verbose_name='Placa do Veículo')

    entry_volume = models.FloatField(verbose_name='Volume de Entrada (m³)')
    moisture = models.FloatField(verbose_name='Umidade (%)')
    fines = models.FloatField(verbose_name='Finos (%)')
    density = models.FloatField(verbose_name='Densidade')

    dcf = models.CharField(max_length=50, verbose_name='DCF')
    gcae = models.CharField(max_length=50, verbose_name='GCAE')

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='charcoal_entries',
        verbose_name='Fornecedor',
    )

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
        validators=[cv.validate_cep],
        help_text='Insira apenas os números.',
        verbose_name='CEP',
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[cv.validate_latitude],
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[cv.validate_longitude],
        null=True,
        blank=True,
    )

    state_registration = models.CharField(max_length=50, verbose_name='Inscrição Estadual', null=True, blank=True)
    municipal_registration = models.CharField(max_length=50, verbose_name='Inscrição Municipal', null=True, blank=True)
    xml_email = models.EmailField(verbose_name='Email XML', null=True, blank=True)

    cpf_cnpj = models.CharField(
        unique=True,
        max_length=14,
        validators=[cv.validate_cpf_cnpj],
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
    )

    def get_documents(self) -> list[Document]:
        return self.documents.all()

    def get_contacts(self) -> list[Contact]:
        return self.contacts.all()

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
