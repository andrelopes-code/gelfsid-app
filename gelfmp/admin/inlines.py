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
