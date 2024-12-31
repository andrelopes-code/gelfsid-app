from django.db import models
from django.forms import ValidationError

from gelfmp.models.charcoal_entry import CharcoalEntry
from gelfmp.utils import validators
from gelfmp.utils.normalization import normalize_file_and_folder

from .base_model import BaseModel


class CharcoalContract(BaseModel):
    def upload_to(instance, _):
        safe_corporate_name = normalize_file_and_folder(instance.supplier.corporate_name)

        contract_name = f'{instance.dcf.process_number}_{instance.supplier.corporate_name}'
        safe_contract_name = normalize_file_and_folder(contract_name)

        return f'fornecedores/{safe_corporate_name}/contratos/{safe_contract_name}'

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.PROTECT,
        related_name='charcoal_contracts',
        verbose_name='Fornecedor',
    )

    dcf = models.ForeignKey(
        'DCF',
        on_delete=models.PROTECT,
        related_name='charcoal_contracts',
        verbose_name='DCF',
    )

    entry_date = models.DateField(null=True, blank=True, verbose_name='Data de Entrada')
    contract_volume = models.FloatField(verbose_name='Volume do Contrato (m³)')
    active = models.BooleanField(default=True, verbose_name='Ativo')

    legal_department_signed = models.BooleanField(default=False, verbose_name='Assinatura do Jurídico')
    supplier_signed = models.BooleanField(default=False, verbose_name='Assinatura do Fornecedor')
    gelf_signed = models.BooleanField(default=False, verbose_name='Assinatura da GELF')

    file = models.FileField(
        upload_to=upload_to,
        null=True,
        blank=True,
        validators=[validators.validate_max_file_size],
        verbose_name='Arquivo de Contrato',
    )

    @property
    def delivered_volume(self):
        entries = CharcoalEntry.objects.filter(dcf=self.dcf)
        return entries.aggregate(models.Sum('entry_volume'))['entry_volume__sum']

    def clean(self):
        if not all([
            self.dcf.declared_volume,
            self.dcf.issue_date,
            self.dcf.validity_date,
            self.dcf.file,
        ]):
            raise ValidationError('Todos os campos da DCF devem estar preenchidos para a criação de um contrato.')

    class Meta:
        verbose_name = 'Contrato de Carvão'
        verbose_name_plural = 'Contratos de Carvão'

    def __str__(self):
        return f'{self.dcf} - {self.supplier}'
