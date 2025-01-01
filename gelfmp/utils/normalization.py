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


def normalize_cep(cep):
    if cep:
        cep = re.sub(r'\D', '', cep)
        cep = cep[:5] + '-' + cep[5:]

    return cep


def normalize_name(name):
    """
    Normaliza um nome, colocando letras maiúsculas no início de cada palavra,
    exceto para conectivos (como "de", "da", "do", "e").
    Preserva palavras inteiramente em maiúsculas (como "LTDA", "JC", "CRP", "CBI").
    """

    if not name:
        return name

    preserve_upper = {
        'LTDA',
        'JC',
        'JA',
        'CRP',
        'CBI',
        'S/A',
        'ME',
        'EPP',
        'CIA',
        'W&D',
        'HF',
        'JK',
        'JF',
        'LHG',
        'EIRELLI',
        'AMM',
        'SA',
        'S.A',
        'S.A.',
        'S/A',
        'HRM',
        'JPL',
        'MG',
    }

    exceptions = {'e', 'de', 'da', 'do', 'das', 'dos'}

    words = name.split()
    normalized_words = []

    for word in words:
        if word.upper() in preserve_upper:
            normalized_words.append(word.upper())

        elif word.lower() in exceptions:
            normalized_words.append(word.lower())

        else:
            normalized_words.append(word.capitalize())

    return ' '.join(normalized_words)


def normalize_file_and_folder(name):
    """Normaliza o nome de arquivos e pastas para uso no sistema de arquivos."""

    if name:
        return re.sub(r'[^a-zA-Z0-9_-]', '_', name)

    return name
