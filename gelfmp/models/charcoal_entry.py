from django.db import models

from gelfmp.utils import validators

from .base import BaseModel


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
