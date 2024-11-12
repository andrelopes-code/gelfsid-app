from venv import logger
import openpyxl as xlsx

from ....models import (
    Cidade,
    FornecedorMateriaPrima,
    Estado,
    RegistroIEF,
    CadastroTecnicoFederal,
    LicencaAmbiental,
)
from .constants import DOCS_PATH, MIN_ROW
from .utils import get_cidade, format_cpf_or_cnpj, get_hyperlink_or_empty, sanitize
from dataclasses import dataclass


@dataclass
class RegistroIEFData:
    doc: str
    hyperlink: str
    validade: str
    status: str


@dataclass
class CadastroTecnicoFederalData:
    doc: str
    hyperlink: str
    validade: str
    status: str


@dataclass
class LicencaAmbientalData:
    doc: str
    hyperlink: str
    validade: str
    status: str


@dataclass
class FornecedorDocRow:
    id: int
    cod_rm: str
    empresa: str
    cidade: str
    cpf_cnpj: str
    estado: str
    produto: str
    licenca: LicencaAmbientalData
    ctf: CadastroTecnicoFederalData
    registro_ief: RegistroIEFData


def run():
    docs_wb = xlsx.load_workbook(DOCS_PATH, data_only=True)
    docs_sheet = docs_wb.active

    if not docs_sheet:
        raise ValueError(f'o documento `{DOCS_PATH}` não tem uma planilha ativa')

    fornecedores = []

    for row in docs_sheet.iter_rows(min_row=MIN_ROW):
        if not row[0].value:
            break

        fornecedor = FornecedorDocRow(
            id=sanitize(row[0].value),
            cod_rm=sanitize(row[1].value),
            empresa=sanitize(row[2].value),
            produto=sanitize(row[6].value),
            cidade='',
            estado='',
            cpf_cnpj=format_cpf_or_cnpj(sanitize(row[11].value)),
            licenca=LicencaAmbientalData(
                doc=sanitize(row[7].value),
                hyperlink=get_hyperlink_or_empty(row[7].value),
                validade=sanitize(row[8].value),
                status=sanitize(row[9].value),
            ),
            ctf=CadastroTecnicoFederalData(
                doc=sanitize(row[10].value),
                hyperlink=get_hyperlink_or_empty(row[10]),
                validade=sanitize(row[12].value),
                status=sanitize(row[13].value),
            ),
            registro_ief=RegistroIEFData(
                doc=sanitize(row[14].value),
                hyperlink=get_hyperlink_or_empty(row[14]),
                validade=sanitize(row[15].value),
                status=sanitize(row[16].value),
            ),
        )

        unidade = row[3].value.split('/')
        cidade = unidade[0].strip()
        estado = unidade[1].strip().upper()

        #! TODO: REMOVER ISSO
        #! TODO: REMOVER ISSO
        #! TODO: REMOVER ISSO
        if estado == 'ME':
            estado = 'MG'

        cidade = get_cidade(cidade, estado)

        fornecedor.cidade = cidade
        fornecedor.estado = estado

        fornecedores.append(fornecedor)

    for fornecedor in fornecedores:
        cidade = Cidade.objects.filter(nome=fornecedor.cidade, estado=fornecedor.estado).first()
        if not cidade:
            logger.error(f'nenhuma cidade encontrada para: {fornecedor.cidade} - {fornecedor.estado}')

        estado = Estado.objects.filter(sigla=fornecedor.estado).first()
        if not estado:
            logger.error(f'nenhum estado encontrado para: {fornecedor.cidade} - {fornecedor.estado}')

        if fornecedor.produto == 'Carvão Vegetal':
            fornecedor.produto = 'CAR'
        elif fornecedor.produto == 'Minério de Ferro':
            fornecedor.produto = 'MIN'
        else:
            continue

        FornecedorMateriaPrima.objects.update_or_create(
            razao_social=fornecedor.empresa,
            cidade=cidade,
            estado=estado,
            tipo_material=fornecedor.produto,
            cpf_cnpj=fornecedor.cpf_cnpj,
        )
