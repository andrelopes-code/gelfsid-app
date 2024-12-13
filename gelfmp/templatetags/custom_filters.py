from django import template
from django.conf import settings
from django.utils import timezone

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

    if len(value) == 11:
        return f'{value[:3]}.{value[3:6]}.{value[6:9]}-{value[9:]}'
    elif len(value) == 14:
        return f'{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}'
    return value
