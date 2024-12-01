from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models


class State(models.Model):
    abbr = models.CharField(max_length=2, primary_key=True, verbose_name='Sigla')
    name = models.CharField(max_length=100, verbose_name='Nome')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')
    state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name='Estado')

    def __str__(self):
        return f'{self.name} - {self.state.abbr}'

    class Meta:
        ordering = ['name']
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'


class Document(models.Model):
    name = models.CharField(max_length=50, verbose_name='Nome')
    type = models.CharField(max_length=50, verbose_name='Tipo de Documento')
    filepath = models.CharField(max_length=255, blank=True, null=True, verbose_name='Link do Arquivo')
    validity = models.DateField(blank=True, null=True, verbose_name='Validade')
    status = models.CharField(max_length=50, verbose_name='Status')

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Fornecedor',
    )

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'


class CharcoalEntry(models.Model):
    entry_date = models.DateField(verbose_name='Data de Entrada')
    origin_ticket = models.CharField(max_length=50, unique=True, verbose_name='Ticket de Origem')
    vehicle_plate = models.CharField(max_length=50, verbose_name='Placa do Veículo')

    entry_volume = models.FloatField(verbose_name='Volume de Entrada')
    moisture = models.FloatField(verbose_name='Umidade')
    fines = models.FloatField(verbose_name='Finos')
    density = models.FloatField(verbose_name='Densidade')

    dcf = models.CharField(max_length=50, verbose_name='DCF')
    gcae = models.CharField(max_length=50, verbose_name='GCAE')

    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='charcoal_entries',
        verbose_name='Fornecedor',
    )

    class Meta:
        ordering = ['-entry_date']
        indexes = [models.Index(fields=['entry_date'])]
        verbose_name = 'Entrada de Carvão'
        verbose_name_plural = 'Entradas de Carvão'


class Supplier(models.Model):
    corporate_name = models.CharField(max_length=200, verbose_name='Razão Social', unique=True)
    material_type = models.CharField(max_length=30, verbose_name='Tipo de Material')
    distance_in_meters = models.IntegerField(blank=True, null=True, verbose_name='Distância em Metros')
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='suppliers', verbose_name='Estado')
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='suppliers', verbose_name='Cidade')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    cpf_cnpj = models.CharField(
        max_length=14,
        unique=True,
        validators=[RegexValidator(r'^(\w{14}|\d{11})$')],
        verbose_name='CPF ou CNPJ',
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        verbose_name='Avaliação',
    )

    def get_documents(self) -> list[Document]:
        return self.documents.all()

    class Meta:
        ordering = ['corporate_name']
        indexes = [
            models.Index(fields=['material_type']),
            models.Index(fields=['state']),
        ]
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'

    def __str__(self):
        return f'{self.corporate_name}'
