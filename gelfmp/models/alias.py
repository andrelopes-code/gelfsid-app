from django.db import models

from .base_model import BaseModel


class Alias(BaseModel):
    alias = models.CharField(
        max_length=255,
        unique=True,
        help_text='Nome alternativo que identifica o fornecedor.',
        verbose_name='Alias',
    )

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='aliases',
        verbose_name='Fornecedor',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'{self.alias} -> {self.supplier}'

    class Meta:
        verbose_name = 'Alias'
        verbose_name_plural = 'Aliases'
