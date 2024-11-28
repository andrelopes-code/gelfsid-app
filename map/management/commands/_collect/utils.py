import heapq
import re
import unicodedata
from datetime import date, datetime

import Levenshtein
import pandas as pd
from rapidfuzz import fuzz

from gelfsid.logger import logger
from map.models import City, State


def datetime_or_none(dt):
    if isinstance(dt, (date, datetime)):
        return dt
    return None


def hyperlink_or_none(cell):
    if hasattr(cell, 'hyperlink') and hasattr(cell.hyperlink, 'target'):
        return cell.hyperlink.target
    return None


def sanitize(value):
    if isinstance(value, str):
        options = {'na', 'n/a', '-', 'não aplicável', 'não aplicavel'}
        if value.strip().lower() in options:
            value = ''
    return value


def normalize_cpf_cnpj(value):
    return re.sub(r'\D', '', value)


def get_db_city(city, state, tolerance_ratio=0.7):
    try:
        db_state = State.objects.filter(abbr=state).first()
        if not db_state:
            raise Exception(f'database state not found: {city} - {state}')

        db_cities = City.objects.filter(name=city, state=state).first()
        if db_cities:
            return db_cities.name

        db_cities = City.objects.filter(state=state).all()

        ratios = []

        for db_city in db_cities:
            ratio = Levenshtein.ratio(city, db_city.name)
            heapq.heappush(ratios, (-ratio, db_city.name))

        if ratios:
            ratio, simiar_city = heapq.heappop(ratios)
            if abs(ratio) > tolerance_ratio:
                return simiar_city

        raise Exception(f'database city not found for: {city} - {state}')

    except Exception as e:
        logger.error(f'error getting city: {e}')


def normalize_text(text):
    if pd.isna(text):
        return ''

    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.lower()

    # Remove caracteres especiais
    text = re.sub(r'[^\w\s]', '', text)

    # Remove palavras desnecessárias
    text = re.sub(r'\b(ltda|sa|fazenda|mina|me|eireli|do|da|de|e|faz.|fazenfa)\b', '', text)

    # Remove espaços extras
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def normalize_and_compare(s1, s2):
    s1 = normalize_text(s1)
    s2 = normalize_text(s2)
    return fuzz.ratio(s1, s2)


def get_best_matches(s, candidates, limit=10):
    return sorted(((normalize_and_compare(s, c), c) for c in candidates), reverse=True)[:limit]
