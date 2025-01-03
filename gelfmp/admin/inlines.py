from gelfmp import models

from .base import BaseTabularInline


class ContactInline(BaseTabularInline):
    model = models.Contact
    extra = 1

    fields = (
        'contact_type',
        'name',
        'email',
        'cpf',
        'primary_phone',
        'secondary_phone',
    )

    verbose_name = 'Contato'
    verbose_name_plural = 'Contatos'


class DocumentInline(BaseTabularInline):
    model = models.Document
    extra = 1

    fields = (
        'visible',
        'document_type',
        'name',
        'validity',
        'file',
    )

    verbose_name = 'Documento'
    verbose_name_plural = 'Documentos'


class BankDetailsInline(BaseTabularInline):
    model = models.BankDetails
    extra = 1
    max_num = 2

    fields = (
        'bank_name',
        'bank_code',
        'account_number',
        'agency',
        'account_cnpj',
    )

    verbose_name = 'Detalhes Bancários'
    verbose_name_plural = 'Detalhes Bancários'


class AliasInline(BaseTabularInline):
    model = models.Alias
    extra = 1

    fields = ('alias',)

    verbose_name = 'Alias'
    verbose_name_plural = 'Aliases'
