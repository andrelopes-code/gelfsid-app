import os

from django.db import models
from django.forms import ValidationError

from gelfcore.logger import log
from gelfmp.services import geojson
from gelfmp.utils import dtutils, validators

from .base import BaseModel
from .choices import DocumentType


class Document(BaseModel):
    def upload_to(instance, filename):
        filename = instance.name + '.' + filename.split('.')[-1] if instance.name else filename
        return f'fornecedores/{instance.supplier.corporate_name}/documentos/{filename}'

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
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Fornecedor',
    )

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    def delete(self, *args, **kwargs):
        try:
            # Remove o arquivo relacionado
            # ao registro de documento caso
            # seja encontrado.
            self.file.close()
            os.remove(self.file.path)

        except PermissionError as e:
            log.error(f'Erro ao tentar deletar arquivo de documento: {e}')
        except FileNotFoundError:
            pass

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
            and self.document_type != DocumentType.OTHER
            and self.document_type != DocumentType.SHAPEFILE
        ):
            self.validity = dtutils.extract_date_from_text(self.filename)

        # Se o documento for um Shapefile obtem o GeoJSON
        # convertendo-o e armazenando no campo geojson.
        if self.document_type == DocumentType.SHAPEFILE:
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
        # Deleta o documento antigo se ao atualizar
        # seja um arquivo de mesmo nome.
        if self.pk:
            try:
                old_file = Document.objects.get(pk=self.pk).file

                if old_file and old_file.name != self.file.name:
                    if os.path.isfile(old_file.path):
                        os.remove(old_file.path)

            except Document.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.document_type} - {self.filename}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
