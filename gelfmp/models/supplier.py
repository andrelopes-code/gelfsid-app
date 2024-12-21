from django.db import models
from django.db.models.query import QuerySet
from django.forms import ValidationError

from gelfmp.utils import validators
from gelfmp.utils.normalization import normalize_text_upper, normalize_to_numbers

from .bank_details import BankDetails
from .base_model import BaseModel
from .charcoal_iqf import CharcoalIQF
from .choices import MaterialType, SupplierType
from .city_state import City, State
from .document import Document


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
        max_length=100,
        choices=SupplierType.choices,
        null=True,
        blank=True,
        verbose_name='Tipo de Fornecedor (Carvão)',
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

    def is_charcoal_supplier(self):
        return self.material_type == MaterialType.CHARCOAL

    def clean(self):
        # Impede que o campo `Tipo de Fornecedor` seja
        # utilizado em fornecedores que não sejam de carvão.
        if self.supplier_type and self.material_type != MaterialType.CHARCOAL:
            raise ValidationError({
                'supplier_type': 'O campo `Tipo de Fornecedor` é exclusivo para fornecedores de carvão.'
            })

        # Garante que o campo `Tipo de Fornecedor` seja
        # preenchido caso seja um fornecedor de carvão.
        if self.material_type == MaterialType.CHARCOAL and not self.supplier_type:
            raise ValidationError({
                'supplier_type': 'O campo `Tipo de Fornecedor` é obrigatório para fornecedores de carvão.'
            })

        return super().clean()

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
