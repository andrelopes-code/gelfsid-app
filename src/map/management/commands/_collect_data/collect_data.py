from django.db import transaction
from gelfsid.logger import logger
import openpyxl
from ....models import (
    Cidade,
    FornecedorMateriaPrima,
    Estado,
    RegistroIEF,
    CadastroTecnicoFederal,
    LicencaAmbiental,
)
from .constants import DOCS_PATH, MIN_ROW
from .utils import datetime_or_none, get_cidade, format_cpf_or_cnpj, hyperlink_or_none, sanitize
from dataclasses import dataclass


@dataclass
class RegistroIEFData:
    documento: str
    hyperlink: str | None
    validade: str | None
    status: str


@dataclass
class CadastroTecnicoFederalData:
    documento: str
    hyperlink: str | None
    validade: str | None
    status: str


@dataclass
class LicencaAmbientalData:
    documento: str
    hyperlink: str | None
    validade: str | None
    status: str


@dataclass
class FornecedorDocRow:
    id: int
    cod_rm: str
    razao_social: str
    cidade: str
    cpf_cnpj: str
    estado: str
    produto: str
    licenca_ambiental: LicencaAmbientalData
    ctf: CadastroTecnicoFederalData
    registro_ief: RegistroIEFData


def run():
    docs_wb = openpyxl.load_workbook(DOCS_PATH, data_only=True)
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
            razao_social=sanitize(row[2].value),
            produto=sanitize(row[6].value),
            cidade='',
            estado='',
            cpf_cnpj=format_cpf_or_cnpj(sanitize(row[11].value)),
            licenca_ambiental=LicencaAmbientalData(
                documento=sanitize(row[7].value),
                hyperlink=hyperlink_or_none(row[7]),
                validade=sanitize(row[8].value),
                status=sanitize(row[9].value),
            ),
            ctf=CadastroTecnicoFederalData(
                documento=sanitize(row[10].value),
                hyperlink=hyperlink_or_none(row[10]),
                validade=sanitize(row[12].value),
                status=sanitize(row[13].value),
            ),
            registro_ief=RegistroIEFData(
                documento=sanitize(row[14].value),
                hyperlink=hyperlink_or_none(row[14]),
                validade=sanitize(row[15].value),
                status=sanitize(row[16].value),
            ),
        )

        unidade = row[3].value.split('/')
        cidade = unidade[0].strip()
        estado = unidade[1].strip().upper()
        cidade = get_cidade(cidade, estado)

        fornecedor.cidade = cidade
        fornecedor.estado = estado

        fornecedores.append(fornecedor)

    registrar_fornecedores(fornecedores)


def registrar_fornecedores(fornecedores: list[FornecedorDocRow]):
    with transaction.atomic():
        for fornecedor in fornecedores:
            cidade = Cidade.objects.filter(nome=fornecedor.cidade, estado=fornecedor.estado).first()
            if not cidade:
                logger.fatal(f'nenhuma cidade encontrada para: {fornecedor.cidade} - {fornecedor.estado}')
                raise ValueError(f'Cidade não encontrada para {fornecedor.cidade} - {fornecedor.estado}')

            estado = Estado.objects.filter(sigla=fornecedor.estado).first()
            if not estado:
                logger.fatal(f'nenhum estado encontrado para: {fornecedor.cidade} - {fornecedor.estado}')
                raise ValueError(f'Estado não encontrado para {fornecedor.cidade} - {fornecedor.estado}')

            if fornecedor.produto == 'Carvão Vegetal':
                fornecedor.produto = 'CAR'
            elif fornecedor.produto == 'Minério de Ferro':
                fornecedor.produto = 'MIN'
            else:
                continue

            db_fornecedor, is_new = FornecedorMateriaPrima.objects.update_or_create(
                razao_social=fornecedor.razao_social,
                cidade=cidade,
                estado=estado,
                tipo_material=fornecedor.produto,
                cpf_cnpj=fornecedor.cpf_cnpj,
            )

            if not fornecedor.licenca_ambiental.documento:
                logger.fatal(f'licença não encontrada para o fornecedor: {fornecedor.razao_social}')
                raise ValueError(f'Licença ambiental não encontrada para {fornecedor.razao_social}')

            if is_new:
                logger.info(f'criado novo fornecedor: {db_fornecedor.razao_social} - {db_fornecedor.cpf_cnpj}')

            db_licenca_ambiental, is_new = LicencaAmbiental.objects.update_or_create(
                documento=fornecedor.licenca_ambiental.documento,
                hyperlink=fornecedor.licenca_ambiental.hyperlink,
                validade=datetime_or_none(fornecedor.licenca_ambiental.validade),
                status=fornecedor.licenca_ambiental.status,
                fornecedor=db_fornecedor,
            )

            db_fornecedor.licenca_ambiental = db_licenca_ambiental

            if fornecedor.ctf.documento:
                db_ctf, is_new = CadastroTecnicoFederal.objects.update_or_create(
                    documento=fornecedor.ctf.documento,
                    hyperlink=fornecedor.ctf.hyperlink,
                    validade=datetime_or_none(fornecedor.ctf.validade),
                    status=fornecedor.ctf.status,
                    fornecedor=db_fornecedor,
                )

                db_fornecedor.cadastro_tecnico_federal = db_ctf

            if fornecedor.registro_ief.documento:
                db_registro_ief, is_new = RegistroIEF.objects.update_or_create(
                    documento=fornecedor.registro_ief.documento,
                    hyperlink=fornecedor.registro_ief.hyperlink,
                    validade=datetime_or_none(fornecedor.registro_ief.validade),
                    status=fornecedor.registro_ief.status,
                    fornecedor=db_fornecedor,
                )

                db_fornecedor.registro_ief = db_registro_ief

            db_fornecedor.save()
