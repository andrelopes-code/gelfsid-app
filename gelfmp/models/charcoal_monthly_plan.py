from django.db import models
from django.forms import ValidationError

from .base_model import BaseModel
from .choices import MonthType, year_choices


class CharcoalMonthlyPlan(BaseModel):
    planned_volume = models.FloatField(verbose_name='Volume Programado (m³)')
    month = models.IntegerField(choices=MonthType.choices, verbose_name='Mês')
    year = models.IntegerField(choices=year_choices(), verbose_name='Ano')

    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Preço (R$)',
        help_text='Somente aplicável a GELF.',
    )

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='monthly_plans',
        verbose_name='Fornecedor',
    )

    def clean(self):
        # Validação do campo 'price' com base no nome do fornecedor,
        # o campo preço é aplicável apenas a própria GELF.
        if self.price is not None and 'GELF' not in self.supplier.corporate_name.upper():
            raise ValidationError({'price': 'O campo `Preço` não é aplicavel a esse fornecedor.'})

        return super().clean()

    def __str__(self):
        return f'{self.supplier} - {self.month}/{self.year}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['supplier', 'month', 'year'],
                name='charcoal_monthly_plan_supplier_month_year_unique_constraint',
            )
        ]
        verbose_name = 'Programação de Carvão'
        verbose_name_plural = 'Programações de Carvão'
