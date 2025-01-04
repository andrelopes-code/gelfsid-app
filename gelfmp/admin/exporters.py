import csv

from django.contrib import admin
from django.db.models import ForeignKey, OneToOneField
from django.http import HttpResponse


class ExportCSV:
    csv_fields = None
    csv_excluded_fields = set()
    csv_delimiter = ','

    @admin.action(description='Exportar para CSV')
    def export_to_csv(self, _, queryset):
        """
        Action para exportar um conjunto de registros para CSV

        Args:
            queryset: conjunto de dados selecionados.

        Returns:
            HttpResponse contendo o arquivo CSV.
        """

        # Objeto de response para o arquivo CSV.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'

        writer = csv.writer(response, delimiter=self.csv_delimiter)

        fields_to_export = self.get_csv_fields()

        # Define os cabeçalhos do arquivo CSV como os nomes
        # 'display' das colunas do banco de dados, ou com o
        # nome personalizado passado em uma tupla em `csv_fields`.
        headers = [
            field[1].upper() if isinstance(field, (tuple, list)) else self.get_field_verbose_name(field).upper()
            for field in fields_to_export
        ]

        # Define o nome real dos campos definidos na tabela do banco, eliminando possiveis tuplas/listas existentes.
        field_names = [field[0] if isinstance(field, (tuple, list)) else field for field in fields_to_export]

        writer.writerow(headers)

        for obj in queryset:
            writer.writerow([self.get_field_value(obj, field) for field in field_names])

        return response

    def get_csv_fields(self):
        """
        Retorna os campos configurados para exportação.
        """

        if self.csv_fields:
            return self.csv_fields

        return [
            field.name
            for field in self.model._meta.get_fields()
            if not field.many_to_many and field.name not in self.csv_excluded_fields
        ]

    def get_field_verbose_name(self, field_path):
        """
        Retorna o verbose_name de um campo,
        suportando campos relacionados.
        """

        field = self.get_field(field_path)
        return field.verbose_name if hasattr(field, 'verbose_name') else field_path

    def get_field(self, field_path):
        """
        Retorna o campo correspondente ao caminho
        informado, suportando campos relacionados.
        """

        model = self.model

        for part in field_path.split('__'):
            field = model._meta.get_field(part)

            if isinstance(field, (ForeignKey, OneToOneField)):
                model = field.related_model

        return field

    def get_field_value(self, obj, field_path):
        """
        Retorna o valor de um campo (suportando caminhos para campos relacionados).
        """

        parts = field_path.split('__')
        for part in parts:
            obj = getattr(obj, part, None)
            if obj is None:
                return ''
        return obj
