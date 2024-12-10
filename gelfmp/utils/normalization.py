import re
import unicodedata


def normalize_text_upper(name):
    """Remove caracteres especiais, espaços extras, e coloca em maiúsculas."""

    if name:
        name = unicodedata.normalize('NFKD', name)
        name = re.sub(r'[^\w\s]', '', name)
        return name.upper().strip()

    return name
