from gelfmp import models

from .base import BaseTabularInline


class ContactInline(BaseTabularInline):
    model = models.Contact
    extra = 1
    classes = ('grp-collapse grp-closed',)

    fields = (
        'contact_type',
        'name',
        'email',
        'primary_phone',
        'secondary_phone',
    )

    verbose_name = 'Contato'
    verbose_name_plural = 'Contatos'


class DocumentInline(BaseTabularInline):
    model = models.Document
    extra = 1
    classes = ('grp-collapse grp-closed',)

    fields = ('name', 'type', 'validity', 'filepath')

    verbose_name = 'Documento'
    verbose_name_plural = 'Documentos'