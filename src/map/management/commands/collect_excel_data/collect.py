from datetime import datetime
from typing import Optional

import openpyxl
from django.db import transaction
from pydantic import BaseModel

from ....models import City, Document, State, Supplier
from .constants import DOCUMENTS_SPREADSHEET_PATH, MIN_ROW
from .utils import datetime_or_none, get_db_city, hyperlink_or_none, normalize_cpf_cnpj, sanitize

ENVIRONMENTAL_PERMIT_TYPE = 'LIC. AMBIENTAL'
CTF_TYPE = 'CTF'
REGIEF_TYPE = 'REG IEF'


class DocumentData(BaseModel):
    name: Optional[str]
    status: Optional[str]
    filepath: Optional[str]
    validity: Optional[datetime]
    type: str = ''


class SupplierData(BaseModel):
    id: int
    rm_code: Optional[str]
    corporate_name: str
    city: str
    cpf_cnpj: str
    state: str
    material_type: str
    environmental_permit: DocumentData
    ctf: DocumentData
    regief: DocumentData


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

        supplier = SupplierData(
            id=sanitize(row[0].value),
            rm_code=sanitize(row[1].value),
            corporate_name=sanitize(row[2].value),
            material_type=sanitize(row[6].value),
            city='',
            state='',
            cpf_cnpj=normalize_cpf_cnpj(sanitize(row[11].value)),
            environmental_permit=DocumentData(
                name=sanitize(row[7].value),
                filepath=hyperlink_or_none(row[7]),
                validity=datetime_or_none(sanitize(row[8].value)),
                status=sanitize(row[9].value),
                type=ENVIRONMENTAL_PERMIT_TYPE,
            ),
            ctf=DocumentData(
                name=sanitize(row[10].value),
                filepath=hyperlink_or_none(row[10]),
                validity=datetime_or_none(sanitize(row[12].value)),
                status=sanitize(row[13].value),
                type=CTF_TYPE,
            ),
            regief=DocumentData(
                name=sanitize(row[14].value),
                filepath=hyperlink_or_none(row[14]),
                validity=datetime_or_none(sanitize(row[15].value)),
                status=sanitize(row[16].value),
                type=REGIEF_TYPE,
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


def save_suppliers(suppliers: list[SupplierData]):
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

            db_supplier = Supplier.objects.filter(
                cpf_cnpj=supplier.cpf_cnpj,
            ).first()

            if not db_supplier:
                db_supplier = Supplier.objects.create(
                    corporate_name=supplier.corporate_name,
                    city=db_city,
                    state=db_state,
                    material_type=supplier.material_type,
                    cpf_cnpj=supplier.cpf_cnpj,
                )
                print(f'created new supplier: {db_supplier.corporate_name} - {db_supplier.cpf_cnpj}')

            if not supplier.environmental_permit.name:
                error_message = f'environmental permit not found for: {supplier.corporate_name}'
                raise ValueError(error_message)

            create_or_update_document(db_supplier, supplier.environmental_permit, ENVIRONMENTAL_PERMIT_TYPE)
            create_or_update_document(db_supplier, supplier.ctf, CTF_TYPE)
            create_or_update_document(db_supplier, supplier.regief, REGIEF_TYPE)

            db_supplier.save()


def create_or_update_document(supplier, document_data: DocumentData, doc_type: str):
    if not document_data.name:
        return

    existing_document = Document.objects.filter(supplier=supplier, type=doc_type).first()
    print(document_data.filepath)
    if existing_document:
        print(f'updating document: {existing_document.name} for supplier: {supplier.id}')

        existing_document.name = document_data.name
        existing_document.validity = document_data.validity
        existing_document.status = document_data.status
        existing_document.filepath = document_data.filepath
        existing_document.save()
    else:
        Document.objects.create(
            supplier=supplier,
            type=doc_type,
            name=document_data.name,
            validity=document_data.validity,
            status=document_data.status,
            filepath=document_data.filepath,
        )
