from django.db import models

from gelfmp.utils import validators

from .base_model import BaseModel
from .choices import MonthType, year_choices


class CharcoalIQF(BaseModel):
    iqf = models.FloatField(verbose_name='IQF')

    planned_percentage = models.FloatField(
        validators=[validators.validate_percentage], verbose_name='Programação Realizada (%)'
    )

    fines_percentage = models.FloatField(validators=[validators.validate_percentage], verbose_name='Finos (%)')
    moisture_percentage = models.FloatField(validators=[validators.validate_percentage], verbose_name='Umidade (%)')
    density_percentage = models.FloatField(validators=[validators.validate_percentage], verbose_name='Densidade (%)')

    volume_density_below_min = models.FloatField(verbose_name='Volume com Densidade Fora (m³)')
    volume_fines_above_max = models.FloatField(verbose_name='Volume com Finos Fora (m³)')
    volume_moisture_above_max = models.FloatField(verbose_name='Volume com Umidade Fora (m³)')
    planned_volume = models.FloatField(verbose_name='Volume Programado (m³)')
    total_volume = models.FloatField(verbose_name='Volume Total (m³)')

    month = models.IntegerField(choices=MonthType.choices, verbose_name='Mês')
    year = models.IntegerField(choices=year_choices(), verbose_name='Ano')

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='iqfs',
        verbose_name='Fornecedor',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['supplier', 'month', 'year'],
                name='charcoal_iqf_supplier_month_year_unique_constraint',
            )
        ]

        ordering = ['-year', '-month']

        verbose_name = 'IQF de Fornecedor de Carvão'
        verbose_name_plural = 'IQFs de Fornecedores de Carvão'
