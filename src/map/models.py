from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator


class Estado(models.Model):
    sigla = models.CharField(max_length=2, primary_key=True)
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome']


class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nome} - {self.estado.sigla}'

    class Meta:
        ordering = ['nome']


class FornecedorMateriaPrima(models.Model):
    TIPO_MATERIAL_CHOICES = [
        ('CAR', 'Carvão Vegetal'),
        ('MIN', 'Minério'),
    ]

    razao_social = models.CharField(max_length=200, verbose_name='Razão Social')
    cnpj = models.CharField(max_length=14, unique=True, validators=[RegexValidator(r'^\w{14}$')], verbose_name='CNPJ')
    tipo_material = models.CharField(max_length=3, choices=TIPO_MATERIAL_CHOICES, verbose_name='Tipo de Material')

    certificacao_ambiental = models.BooleanField(default=False, verbose_name='Certificação Ambiental')
    licenca_operacao = models.CharField(max_length=50, blank=True, verbose_name='Licenca de Operação')
    registro_ibama = models.CharField(max_length=50, blank=True, verbose_name='Registro IBAMA')

    nota_qualidade = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        verbose_name='Nota de Qualidade',
    )

    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name='fornecedores')
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT, related_name='fornecedores')
    coordenadas_gps = models.CharField(max_length=100, blank=True, verbose_name='Coordenadas GPS')
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['razao_social']
        indexes = [
            models.Index(fields=['tipo_material']),
            models.Index(fields=['estado']),
        ]
        verbose_name = 'Fornecedor de Matéria Prima'
        verbose_name_plural = 'Fornecedores de Matéria Prima'

    def __str__(self):
        return f'{self.razao_social} - {self.get_tipo_material_display()} - {self.cnpj}'
