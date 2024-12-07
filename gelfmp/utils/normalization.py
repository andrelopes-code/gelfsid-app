import unicodedata
import re


def normalize_text_upper(name):
    if name:
        name = unicodedata.normalize('NFKD', name)
        name = re.sub(r'[^\w\s]', '', name)
        return name.upper().strip()
    return name
