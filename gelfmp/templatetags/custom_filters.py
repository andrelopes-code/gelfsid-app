from datetime import datetime

from django import template
from django.utils import timezone

from gelfmp.utils.normalization import normalize_to_numbers

register = template.Library()


@register.filter
def comma_to_dot(value):
    return str(value).replace(',', '.')


@register.filter
def get_validity_status(validity_date):
    if not validity_date:
        return 'AUSENTE'

    today = timezone.now().date()
    diff_in_days = (validity_date - today).days

    if diff_in_days < 0:
        return 'VENCIDO'
    elif diff_in_days <= 30:
        return f'VENCE EM {diff_in_days} DIAS'
    else:
        return 'VÁLIDO'


@register.filter
def format_cpf_cnpj(value):
    if not isinstance(value, str):
        return value

    value = normalize_to_numbers(value)

    if len(value) == 11:
        return f'{value[:3]}.{value[3:6]}.{value[6:9]}-{value[9:]}'
    elif len(value) == 14:
        return f'{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}'
    return value


@register.filter
def format_date(date_str):
    formats = ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S.%fZ', '%d/%m/%Y', '%m-%d-%Y']

    for fmt in formats:
        try:
            date = datetime.strptime(date_str, fmt)
            return date.strftime('%d/%m/%Y')

        except ValueError:
            continue

    return date_str


@register.filter
def format_activity_id(value):
    try:
        value = str(value).rjust(7, '0')
        return f'{value[:4]}-{value[4:5]}/{value[5:]}'

    except Exception:
        return value
