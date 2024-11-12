from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator


class InfoRota(models.Model):
    origem = models.CharField(max_length=255)
    destino = models.CharField(max_length=255)
    distancia_em_metros = models.IntegerField()
    duracao_em_segundos = models.IntegerField()

    class Meta:
        unique_together = ('origem', 'destino')
        constraints = [
            models.UniqueConstraint(fields=['origem', 'destino'], name='unique_origem_destino'),
        ]

    def __str__(self):
        return f'{self.origem} -> {self.destino}: {self.distancia_em_metros}m, {self.duracao_em_segundos}s'


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


class LicencaAmbiental(models.Model):
    documento = models.CharField(max_length=50)
    hyperlink = models.CharField(max_length=255, blank=True, null=True)
    validade = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50)

    fornecedor = models.OneToOneField('FornecedorMateriaPrima', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Licença Ambiental'
        verbose_name_plural = verbose_name


class RegistroIEF(models.Model):
    documento = models.CharField(max_length=50)
    hyperlink = models.CharField(max_length=255, blank=True, null=True)
    validade = models.DateField()
    status = models.CharField(max_length=50)

    fornecedor = models.OneToOneField('FornecedorMateriaPrima', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Registro IEF'
        verbose_name_plural = verbose_name


class CadastroTecnicoFederal(models.Model):
    documento = models.CharField(max_length=50)
    hyperlink = models.CharField(max_length=255, blank=True, null=True)
    validade = models.DateField()
    status = models.CharField(max_length=50)

    fornecedor = models.OneToOneField('FornecedorMateriaPrima', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Cadastro Técnico Federal'
        verbose_name_plural = verbose_name


class FornecedorMateriaPrima(models.Model):
    TIPO_MATERIAL_CHOICES = [
        ('CAR', 'Carvão Vegetal'),
        ('MIN', 'Minério'),
    ]

    razao_social = models.CharField(max_length=200, verbose_name='Razão Social')
    cpf_cnpj = models.CharField(
        max_length=14, unique=True, validators=[RegexValidator(r'^(\w{14}|\d{11})$')], verbose_name='CPF ou CNPJ'
    )
    tipo_material = models.CharField(max_length=3, choices=TIPO_MATERIAL_CHOICES, verbose_name='Tipo de Material')

    licenca_ambiental = models.OneToOneField(
        LicencaAmbiental,
        on_delete=models.PROTECT,
        verbose_name='Licenca Ambiental',
        blank=True,
        null=True,
    )

    cadastro_tecnico_federal = models.OneToOneField(
        CadastroTecnicoFederal,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Cadastro Técnico Federal',
    )

    registro_ief = models.OneToOneField(
        RegistroIEF,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Registro IEF',
    )

    avaliacao = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        verbose_name='Avaliação',
    )

    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name='fornecedores')
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT, related_name='fornecedores')
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
        return f'{self.razao_social} - {self.get_tipo_material_display()} - {self.cpf_cnpj}'
