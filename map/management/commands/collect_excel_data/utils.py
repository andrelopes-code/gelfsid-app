import heapq
import re
from datetime import date, datetime

import Levenshtein

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


def is_similar(str_a, str_b, tolerance_ratio=0.8):
    return Levenshtein.ratio(str_a, str_b) > tolerance_ratio


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
