import heapq
import os
import re
import Levenshtein
from gelfsid.logger import logger
from map.models import Cidade, Estado
from .constants import FILES_BASE_PATH
from datetime import datetime, date


def datetime_or_none(dt):
    if isinstance(dt, (date, datetime)):
        return dt
    return None


def hyperlink_or_none(cell):
    if hasattr(cell, 'hyperlink') and hasattr(cell.hyperlink, 'target'):
        return os.path.join(FILES_BASE_PATH, cell.hyperlink.target)
    return None


def sanitize(value):
    if isinstance(value, str):
        value = value.strip()
        if value.lower() in ('na', 'n/a', '-', 'não aplicável', 'não aplicavel'):
            value = ''
    return value


def format_cpf_or_cnpj(value):
    return re.sub(r'\D', '', value)


def is_similar(a, b):
    return Levenshtein.ratio(a, b) > 0.8


def get_cidade(cidade, estado, tolerance_ratio=0.7):
    try:
        db_estado = Estado.objects.filter(sigla=estado).first()
        if not db_estado:
            raise Exception(f'nenhum estado encontrado para: {cidade} - {estado}')

        db_cidade = Cidade.objects.filter(nome=cidade, estado=estado).first()
        if db_cidade:
            return db_cidade.nome

        db_cidades = Cidade.objects.filter(estado=estado).all()
        ratios = []

        for db_cidade in db_cidades:
            ratio = Levenshtein.ratio(cidade, db_cidade.nome)
            heapq.heappush(ratios, (-ratio, db_cidade.nome))

        if ratios:
            ratio, cc = heapq.heappop(ratios)
            if abs(ratio) > tolerance_ratio:
                return cc

        raise Exception(f'nenhuma cidade encontrada para: {cidade} ||| {estado}')

    except Exception as e:
        logger.error(f'erro ao buscar cidade: {e}')
