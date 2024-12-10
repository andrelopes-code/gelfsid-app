from datetime import timedelta

from django.utils.timezone import now


def days_ago(days: int):
    """
    Retorna a data/hora de 'X' dias atrás.
    """
    return now() - timedelta(days=days)


def days_from_now(days: int):
    """
    Retorna a data/hora de 'X' dias no futuro.
    """
    return now() + timedelta(days=days)


def months_ago(months: int):
    """
    Retorna a data/hora de 'X' meses atrás.
    Considera que um mês tem 30 dias para simplificação.
    """
    return now() - timedelta(days=30 * months)


def months_from_now(months: int):
    """
    Retorna a data/hora de 'X' meses no futuro.
    Considera que um mês tem 30 dias para simplificação.
    """
    return now() + timedelta(days=30 * months)


def years_ago(years: int):
    """
    Retorna a data/hora de 'X' anos atrás.
    Considera que um ano tem 365 dias.
    """
    return now() - timedelta(days=365 * years)


def years_from_now(years: int):
    """
    Retorna a data/hora de 'X' anos no futuro.
    Considera que um ano tem 365 dias.
    """
    return now() + timedelta(days=365 * years)


def start_of_today():
    """
    Retorna o início do dia atual (00:00:00).
    """
    current = now()
    return current.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_today():
    """
    Retorna o final do dia atual (23:59:59).
    """
    current = now()
    return current.replace(hour=23, minute=59, second=59, microsecond=999999)


def last_month():
    """
    Retorna o mês anterior ao atual.
    """
    current_month = now().month
    return 12 if current_month == 1 else current_month - 1


def current_year():
    """
    Retorna o ano atual.
    """
    return now().year
