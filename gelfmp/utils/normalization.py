import re
import unicodedata


def normalize_text_upper(name):
    """Remove caracteres especiais, espaços extras, e coloca em maiúsculas."""

    if name:
        name = unicodedata.normalize('NFKD', name)
        name = ''.join(c for c in name if not unicodedata.combining(c))
        name = re.sub(r'[,]', '', name)
        name = re.sub(r'\s+', ' ', name)
        return name.upper().strip()

    return name


def normalize_to_numbers(value):
    """Remove caracteres não numéricos deixando apenas os dígitos. Ex: (123.456.789-00) -> 12345678900."""

    if value:
        return re.sub(r'\D', '', value)
