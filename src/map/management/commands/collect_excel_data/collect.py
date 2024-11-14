from datetime import datetime
from typing import Optional

import openpyxl
from django.db import transaction
from pydantic import BaseModel

from ....models import City, State, Supplier
from .constants import DOCUMENTS_SPREADSHEET_PATH, MIN_ROW
from .utils import datetime_or_none, get_db_city, hyperlink_or_none, normalize_cpf_cnpj, sanitize


class Document(BaseModel):
    document: Optional[str]
    status: Optional[str]
    filepath: Optional[str]
    validity: Optional[datetime]
    type: str = ''


class SupplierDocRow(BaseModel):
    id: int
    rm_code: Optional[str]
    corporate_name: str
    city: str
    cpf_cnpj: str
    state: str
    material_type: str
    environmental_permit: Document
    ctf: Document
    regief: Document


def run():
    documents_workbook = openpyxl.load_workbook(DOCUMENTS_SPREADSHEET_PATH, data_only=True)
    documents_sheet = documents_workbook.active

    if not documents_sheet:
        raise ValueError(f'document `{DOCUMENTS_SPREADSHEET_PATH}` does not have an active sheet')

    suppliers = []

    for row in documents_sheet.iter_rows(min_row=MIN_ROW):
        # break if is an empty row
        if not row[0].value:
            break

        supplier = SupplierDocRow(
            id=sanitize(row[0].value),
            rm_code=sanitize(row[1].value),
            corporate_name=sanitize(row[2].value),
            material_type=sanitize(row[6].value),
            city='',
            state='',
            cpf_cnpj=normalize_cpf_cnpj(sanitize(row[11].value)),
            environmental_permit=Document(
                document=sanitize(row[7].value),
                filepath=hyperlink_or_none(row[7]),
                validity=datetime_or_none(sanitize(row[8].value)),
                status=sanitize(row[9].value),
            ),
            ctf=Document(
                document=sanitize(row[10].value),
                filepath=hyperlink_or_none(row[10]),
                validity=datetime_or_none(sanitize(row[12].value)),
                status=sanitize(row[13].value),
            ),
            regief=Document(
                document=sanitize(row[14].value),
                filepath=hyperlink_or_none(row[14]),
                validity=datetime_or_none(sanitize(row[15].value)),
                status=sanitize(row[16].value),
            ),
        )

        city_state = row[3].value.split('/')
        city = city_state[0].strip()
        state = city_state[1].strip().upper()

        # try to get an existing city in
        # the database that matches
        city = get_db_city(city, state)

        supplier.city = city
        supplier.state = state

        suppliers.append(supplier)
    save_suppliers(suppliers)


def save_suppliers(suppliers: list[SupplierDocRow]):
    with transaction.atomic():
        for supplier in suppliers:
            db_city = City.objects.filter(name=supplier.city, state=supplier.state).first()
            if not db_city:
                error_message = f'database city not found for: {supplier.city} - {supplier.state}'
                raise ValueError(error_message)

            db_state = State.objects.filter(abbr=supplier.state).first()
            if not db_state:
                error_message = f'database state not found for: {supplier.city} - {supplier.state}'
                raise ValueError(error_message)

            if supplier.material_type == 'Carvão Vegetal':
                supplier.material_type = 'CAR'
            elif supplier.material_type == 'Minério de Ferro':
                supplier.material_type = 'MIN'
            else:
                continue

            db_supplier, new = Supplier.objects.update_or_create(
                corporate_name=supplier.corporate_name,
                city=db_city,
                state=db_state,
                material_type=supplier.material_type,
                cpf_cnpj=supplier.cpf_cnpj,
            )

            if not supplier.environmental_permit.document:
                error_message = f'environmental permit not found for: {supplier.corporate_name}'
                raise ValueError(error_message)

            if new:
                print(f'created new supplier: {db_supplier.corporate_name} - {db_supplier.cpf_cnpj}')

            db_supplier.save()
