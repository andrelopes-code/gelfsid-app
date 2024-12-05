from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

validate_cpf_cnpj = RegexValidator(
    regex=r'^(\w{14}|\d{11})$',
    message='Insira um CPF ou CNPJ válido, digitando apenas os números.',
)

validate_cep = RegexValidator(
    regex=r'^\d{8}$',
    message='Insira um CEP válido, digitando apenas os números.',
)


def validate_latitude(value):
    if value < -90 or value > 90:
        raise ValidationError('Latitude deve estar entre -90 e 90 graus.')


def validate_longitude(value):
    if value < -180 or value > 180:
        raise ValidationError('Longitude deve estar entre -180 e 180 graus.')
