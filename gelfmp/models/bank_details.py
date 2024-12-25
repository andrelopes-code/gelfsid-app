from django.db import models

from gelfmp.utils import validators
from gelfmp.utils.normalization import normalize_text_upper

from .base_model import BaseModel


class BankDetails(BaseModel):
    bank_name = models.CharField(max_length=255, verbose_name='Banco')
    agency = models.CharField(max_length=10, verbose_name='Agência')
    account_number = models.CharField(max_length=20, verbose_name='Número da Conta')

    account_cnpj = models.CharField(
        max_length=20,
        validators=[validators.validate_cnpj],
        verbose_name='CNPJ da Conta',
        null=True,
        blank=True,
    )

    bank_code = models.CharField(
        max_length=5,
        validators=[validators.validate_bank_code],
        verbose_name='Número do Banco',
    )

    supplier = models.OneToOneField(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='bank_details',
        verbose_name='Fornecedor',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'{self.supplier} - {self.bank_name} - Cc: {self.account_number} Ag: {self.agency}'

    def save(self, *args, **kwargs):
        # Normaliza o nome do banco antes de salvar o registro.
        self.bank_name = normalize_text_upper(self.bank_name)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Detalhes Bancários'
        verbose_name_plural = 'Detalhes Bancários'
        ordering = ['bank_name']
