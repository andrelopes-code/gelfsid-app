import os

from django.db import models
from django.forms import ValidationError

from gelfmp.services import geojson
from gelfmp.utils import dtutils, validators
from gelfmp.utils.functions import handle_file_cleanup, handle_file_cleanup_on_delete
from gelfmp.utils.normalization import normalize_file_and_folder

from .base_model import BaseModel
from .choices import DocumentType


class Document(BaseModel):
    def upload_to(instance, filename):
        safe_filename = normalize_file_and_folder(filename)
        safe_corporate_name = normalize_file_and_folder(instance.supplier.corporate_name)

        return f'FORNECEDORES/{safe_corporate_name}/DOCUMENTOS/{safe_filename}'

    name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Nome de Exibição',
        help_text='Caso não informado, o nome do arquivo será usado para preencher este campo.',
    )

    file = models.FileField(
        upload_to=upload_to,
        max_length=255,
        verbose_name='Arquivo',
        validators=[validators.validate_max_file_size],
    )

    geojson = models.JSONField(
        blank=True,
        null=True,
        verbose_name='GeoJSON',
        help_text='Este campo é gerado automaticamente ao subir um Shapefile e não deve ser alterado manualmente.',
    )

    validity = models.DateField(
        blank=True,
        null=True,
        verbose_name='Validade',
        help_text=(
            'Caso não informado e o nome do arquivo contém a data, ela será usada para preencher este campo.\n'
            'Exemplo: nome do arquivo CTF_02.05.2020.pdf, a data 02/05/2020 será usada.'
        ),
    )

    document_type = models.CharField(max_length=50, choices=DocumentType.choices, verbose_name='Tipo de Documento')
    visible = models.BooleanField(default=True, verbose_name='Visível')

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.PROTECT,
        related_name='documents',
        verbose_name='Fornecedor',
    )

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    def delete(self, *args, **kwargs):
        handle_file_cleanup_on_delete(self)
        super().delete(*args, **kwargs)

    def clean(self):
        # Caso não seja informado um nome de exibição
        # usar o próprio nome do arquivo.
        if not self.name:
            self.name = self.filename

        # Tenta extrair a data de validade do nome do
        # arquivo caso ela não seja informada.
        if (
            not self.validity
            and self.document_type != DocumentType.EXCEMPTION
            and self.document_type != DocumentType.CAR
            and self.document_type != DocumentType.SHAPEFILE
            and self.document_type != DocumentType.PROPERTY_SHAPEFILE
            and self.document_type != DocumentType.OTHER
        ):
            self.validity = dtutils.extract_date_from_text(self.filename)

            if not self.validity:
                raise ValidationError('Informe uma data de validade para este documento.')

        if self.document_type == DocumentType.SHAPEFILE or self.document_type == DocumentType.PROPERTY_SHAPEFILE:
            # Define a visibibilidade para todos
            # os Shapefiles como falso.
            self.visible = False

            if self.document_type == DocumentType.PROPERTY_SHAPEFILE:
                # Verificar se já existe um Shapefile de Propriedade
                # registrado para esse fornecedor de carvão.
                if Document.objects.filter(
                    document_type=DocumentType.PROPERTY_SHAPEFILE,
                    supplier=self.supplier,
                ).exists():
                    raise ValidationError('O fornecedor ja possui um Shapefile de Propriedade.')

            if self.file:
                try:
                    if self.file.name.lower().endswith('.zip'):
                        self.geojson = geojson.from_shapefile_zip(self.file)
                    else:
                        raise ValidationError('O arquivo enviado deve ser um arquivo ZIP válido.')

                except ValidationError as e:
                    raise e

        return super().clean()

    def save(self, *args, **kwargs):
        handle_file_cleanup(self)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.document_type} - {self.filename}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
