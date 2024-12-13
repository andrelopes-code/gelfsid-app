import openpyxl
from django.db import transaction

from gelfmp.models import City, Document, MaterialType, State, Supplier

from .constants import CTF_TYPE, ENVIRONMENTAL_PERMIT_TYPE, REGIEF_TYPE, SUPPLIERS_DOCS_PATH
from .types import DocumentData, SupplierData
from .utils import datetime_or_none, get_db_city, hyperlink_or_none, normalize_cpf_cnpj, rmna

MIN_ROW = 17


def collect():
    documents_workbook = openpyxl.load_workbook(SUPPLIERS_DOCS_PATH, data_only=True)
    documents_sheet = documents_workbook.active

    if not documents_sheet:
        raise ValueError(f'document `{SUPPLIERS_DOCS_PATH}` does not have an active sheet')

    suppliers = []

    for row in documents_sheet.iter_rows(min_row=MIN_ROW):
        # Interrompe o loop quando a primeira coluna estiver vazia
        if not row[0].value:
            break

        # Verifica se a linha corresponde a um CLIENTE e a ignora
        if row[4].value:
            continue

        supplier = SupplierData(
            id=rmna(row[0].value),
            rm_code=rmna(row[1].value),
            corporate_name=rmna(row[2].value),
            material_type=rmna(row[6].value),
            city='',
            state='',
            cpf_cnpj=normalize_cpf_cnpj(rmna(row[11].value)),
            environmental_permit=DocumentData(
                name=rmna(row[7].value),
                filepath=hyperlink_or_none(row[7]),
                validity=datetime_or_none(rmna(row[8].value)),
                status=rmna(row[9].value),
                type=ENVIRONMENTAL_PERMIT_TYPE,
            ),
            ctf=DocumentData(
                name=rmna(row[10].value),
                filepath=hyperlink_or_none(row[10]),
                validity=datetime_or_none(rmna(row[12].value)),
                status=rmna(row[13].value),
                type=CTF_TYPE,
            ),
            regief=DocumentData(
                name=rmna(row[14].value),
                filepath=hyperlink_or_none(row[14]),
                validity=datetime_or_none(rmna(row[15].value)),
                status=rmna(row[16].value),
                type=REGIEF_TYPE,
            ),
        )

        city_state = row[3].value.split('/')
        city = city_state[0].strip()
        state = city_state[1].strip().upper()

        # Tenta encontrar uma cidade
        # existente no banco de dados
        city = get_db_city(city, state)

        supplier.city = city
        supplier.state = state

        for name, value in MaterialType.choices:
            if supplier.material_type == value:
                supplier.material_type = name
                break
        else:
            raise ValueError(f'MaterialType ({supplier.material_type}) not found in choices: {MaterialType.choices}')

        suppliers.append(supplier)
    save_suppliers(suppliers)


def save_suppliers(suppliers: list[SupplierData]):
    with transaction.atomic():
        for supplier in suppliers:
            db_city = City.objects.filter(name=supplier.city, state=supplier.state).first()
            if not db_city:
                raise ValueError(f'database city not found for: {supplier.city} - {supplier.state}')

            db_state = State.objects.filter(abbr=supplier.state).first()
            if not db_state:
                raise ValueError(f'database state not found for: {supplier.city} - {supplier.state}')

            db_supplier = Supplier.objects.filter(
                cpf_cnpj=supplier.cpf_cnpj,
            ).first()

            db_supplier, created = Supplier.objects.update_or_create(
                cpf_cnpj=supplier.cpf_cnpj,
                defaults={
                    'corporate_name': supplier.corporate_name,
                    'city': db_city,
                    'state': db_state,
                    'material_type': supplier.material_type,
                    'cpf_cnpj': supplier.cpf_cnpj,
                },
            )

            if created:
                print(f'created new supplier: {db_supplier.corporate_name} - {db_supplier.cpf_cnpj}')

            if not supplier.environmental_permit.name:
                raise ValueError(f'environmental permit not found for: {supplier.corporate_name}')

            # ? Ignorar documentos
            # create_or_update_document(db_supplier, supplier.environmental_permit, ENVIRONMENTAL_PERMIT_TYPE)
            # create_or_update_document(db_supplier, supplier.ctf, CTF_TYPE)
            # create_or_update_document(db_supplier, supplier.regief, REGIEF_TYPE)

            db_supplier.save()


def create_or_update_document(supplier, document_data: DocumentData, doc_type: str):
    if not document_data.name:
        return

    document, created = Document.objects.update_or_create(
        supplier=supplier,
        type=doc_type,
        defaults={
            'name': document_data.name,
            'validity': document_data.validity,
            'filepath': document_data.filepath,
        },
    )

    if created:
        print(f'Created new document: {document.name} for supplier: {supplier.id}')
    else:
        print(f'Updated document: {document.name} for supplier: {supplier.id}')
