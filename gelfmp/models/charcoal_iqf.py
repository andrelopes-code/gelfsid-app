from django.db import models

from gelfmp.utils import validators

from .base import BaseModel
from .choices import MonthType, year_choices


class CharcoalIQF(BaseModel):
    iqf = models.FloatField(verbose_name='IQF')

    planned_percentage = models.FloatField(
        validators=[validators.validate_percentage], verbose_name='Programação Realizada (%)'
    )

    fines_percentage = models.FloatField(validators=[validators.validate_percentage], verbose_name='Finos (%)')
    moisture_percentage = models.FloatField(validators=[validators.validate_percentage], verbose_name='Umidade (%)')
    density_percentage = models.FloatField(validators=[validators.validate_percentage], verbose_name='Densidade (%)')

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
        verbose_name = 'IQF de Fornecedor de Carvão'
        verbose_name_plural = 'IQFs de Fornecedores de Carvão'
