from django.db import models

from gelfmp.utils import validators
from gelfmp.utils.normalization import normalize_name, normalize_phone

from .base import BaseModel
from .choices import ContactType


class Contact(BaseModel):
    name = models.CharField(max_length=200, verbose_name='Nome')
    cpf = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        validators=[validators.validate_cpf_cnpj],
        verbose_name='CPF',
    )

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

    def clean(self):
        self.primary_phone = normalize_phone(self.primary_phone)
        self.secondary_phone = normalize_phone(self.secondary_phone)
        self.name = normalize_name(self.name)

        return super().clean()

    def __str__(self):
        return f'{self.contact_type} - {self.name}'

    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
