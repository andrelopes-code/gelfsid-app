import re
import unicodedata


def normalize_text_upper(name):
    """Remove caracteres especiais, espaços extras, e coloca em maiúsculas."""

    if name:
        name = unicodedata.normalize('NFKD', name)
        name = ''.join(c for c in name if not unicodedata.combining(c))
        name = re.sub(r'[,/]', '', name)
        name = re.sub(r'\s+', ' ', name)
        return name.upper().strip()

    return name


def normalize_to_numbers(value):
    """Remove caracteres não numéricos deixando apenas os dígitos. Ex: (123.456.789-00) -> 12345678900."""

    if value:
        return re.sub(r'\D', '', value)


def normalize_phone(phone):
    """Retorna o telefone formatado. Ex: 31996990146 -> (31) 99699-0146."""

    if phone:
        phone_digits = re.sub(r'\D', '', phone)

        if len(phone_digits) == 8:
            return f'{phone_digits[:4]}-{phone_digits[4:]}'
        elif len(phone_digits) == 9:
            return f'{phone_digits[:5]}-{phone_digits[5:]}'
        elif len(phone_digits) == 10:
            return f'({phone_digits[:2]}) {phone_digits[2:6]}-{phone_digits[6:]}'
        elif len(phone_digits) == 11:
            return f'({phone_digits[:2]}) {phone_digits[2:7]}-{phone_digits[7:]}'

    return phone


def normalize_name(name):
    """
    Normaliza um nome, colocando letras maiúsculas no início de cada palavra,
    exceto para conectivos (como "de", "da", "do", "e").
    """

    if not name:
        return name

    exceptions = {'e', 'de', 'da', 'do', 'das', 'dos'}

    words = name.split()
    normalized_words = [word.capitalize() if word.lower() not in exceptions else word.lower() for word in words]

    if normalized_words:
        normalized_words[0] = normalized_words[0].capitalize()

    return ' '.join(normalized_words)
