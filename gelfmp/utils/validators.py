from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

validate_cpf_cnpj = RegexValidator(
    regex=r'^(\w{14}|\d{11}|\d{3}.\d{3}.\d{3}-\d{2}|\d{2}.\d{3}.\d{3}/\d{4}-\d{2})$',
    message='Insira um CPF ou CNPJ válido. Use apenas numeros ou 000.000.000-00, 00.000.000/0000-00.',
)

validate_cep = RegexValidator(
    regex=r'^(\d{8}|\d{5}-\d{3})$',
    message='Insira um CEP válido. Use o formato 00000000 ou 00000-000.',
)

validate_dcf = RegexValidator(
    regex=r'^\d{13}/\d{2}-\d{2}$',
    message='Insira uma DCF válida, usando o formato 0000000000000/00-00.',
)

validate_bank_code = RegexValidator(
    regex=r'^\d{3}',
    message='Insira um número válido, usando o formato 000 (3 dígitos).',
)


def validate_percentage(value):
    if not (0 <= value <= 100):
        raise ValidationError('O valor deve estar entre 0 e 100.')


def validate_latitude(value):
    if value < -90 or value > 90:
        raise ValidationError('Latitude deve estar entre -90 e 90 graus.')


def validate_longitude(value):
    if value < -180 or value > 180:
        raise ValidationError('Longitude deve estar entre -180 e 180 graus.')


def validate_max_file_size(mbsize):
    def validate_file_size(file):
        bsize = mbsize * 1024 * 1024

        if file.size > bsize:
            raise ValidationError(f'O arquivo não pode exceder {mbsize}MB.')

    return validate_file_size
