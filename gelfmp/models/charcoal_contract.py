import os

from django.db import models
from django.forms import ValidationError

from gelfmp.models.charcoal_entry import CharcoalEntry
from gelfmp.utils import validators
from gelfmp.utils.functions import handle_file_cleanup, handle_file_cleanup_on_delete
from gelfmp.utils.normalization import normalize_file_and_folder

from .base_model import BaseModel


class CharcoalContract(BaseModel):
    def upload_to(instance, filename):
        safe_corporate_name = normalize_file_and_folder(instance.supplier.corporate_name)

        contract_name = f'{instance.dcf.process_number}_{instance.supplier.corporate_name}'
        safe_contract_name = normalize_file_and_folder(contract_name)
        file_extension = os.path.splitext(filename)[1]

        return f'FORNECEDORES/{safe_corporate_name}/CONTRATOS/{safe_contract_name}.{file_extension}'

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
    price = models.FloatField(verbose_name='Preço (R$)')
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

    @property
    def price_per_ton(self):
        # Preço dividido pela densidade de corte.
        return round(self.price / 0.235, 2)

    def clean(self):
        try:
            if not all([
                self.dcf.declared_volume,
                self.dcf.issue_date,
                self.dcf.validity_date,
                self.dcf.file,
            ]):
                raise ValidationError('Todos os campos da DCF devem estar preenchidos para a criação de um contrato.')

            if self.supplier != self.dcf.supplier:
                raise ValidationError('O fornecedor do contrato deve ser o mesmo fornecedor do DCF.')

        except Exception as e:
            raise ValidationError(f'Erro ao criar o contrato: {e}')

        if not self.entry_date:
            first_entry = self.dcf.charcoal_entries.order_by('entry_date').first()
            if first_entry:
                self.entry_date = first_entry.entry_date

        return super().clean()

    def delete(self, *args, **kwargs):
        handle_file_cleanup_on_delete(self)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        handle_file_cleanup(self)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Contrato de Carvão'
        verbose_name_plural = 'Contratos de Carvão'

    def __str__(self):
        return f'{self.dcf} - {self.supplier}'
