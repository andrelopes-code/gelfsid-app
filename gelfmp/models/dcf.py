from datetime import timedelta

from django.db import models

from gelfmp.utils import validators
from gelfmp.utils.normalization import normalize_file_and_folder

from .base_model import BaseModel


class DCF(BaseModel):
    def upload_to(instance, _):
        safe_corporate_name = normalize_file_and_folder(instance.supplier.corporate_name)
        safe_process_number = normalize_file_and_folder(instance.process_number)

        return f'fornecedores/{safe_corporate_name}/dcfs/{safe_process_number}'

    process_number = models.CharField(
        max_length=50,
        validators=[validators.validate_dcf],
        verbose_name='Número do Processo',
    )

    declared_volume = models.FloatField(null=True, blank=True, verbose_name='Volume Declarado (m³)')
    issue_date = models.DateField(null=True, blank=True, verbose_name='Data de Emissão')
    validity_date = models.DateField(null=True, blank=True, editable=False, verbose_name='Data de Vencimento')

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.PROTECT,
        related_name='dcfs',
        verbose_name='Fornecedor',
    )

    file = models.FileField(
        upload_to=upload_to,
        validators=[validators.validate_max_file_size],
        null=True,
        blank=True,
        verbose_name='Arquivo DCF',
    )

    def clean(self):
        # Define a validade da DCF com base na data de
        # emissão sendo essa validade de exatamente 3 anos.
        if self.issue_date:
            self.validity_date = self.issue_date + timedelta(days=365 * 3)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['process_number'],
                name='dcf_process_number_unique_constraint',
            )
        ]

        verbose_name = 'DCF'
        verbose_name_plural = 'DCFs'

    def __str__(self):
        return f'{self.process_number}'
