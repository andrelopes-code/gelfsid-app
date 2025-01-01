from datetime import datetime
from unittest.mock import MagicMock

import pytest

from gelfmp.services.contract_filler import ContractFillerService


def get_supplier_and_contract_mock():
    supplier = MagicMock(
        corporate_name='CBI MADEIRAS LTDA - FAZENDA CORPO DOS PORCOS',
        cep='12345678',
        cpf_cnpj='12345678901234',
        city=MagicMock(name='Belo Horizonte', state=MagicMock(abbr='MG')),
        bank_details=MagicMock(
            bank_name='BANCO DO BRASIL',
            account_number='123456789',
            agency='1234',
        ),
    )

    contract = MagicMock(
        id=1,
        contract_volume=1234,
        price=200,
        entry_date=datetime(2024, 11, 23),
        dcf=MagicMock(process_number='123456789'),
        supplier=supplier,
    )

    return supplier, contract


@pytest.mark.django_db
def test_context_keys():
    filler = ContractFillerService()
    supplier, contract = get_supplier_and_contract_mock()

    context = filler.build_context(supplier, contract)

    assert list(context.keys()) == [
        'header_id',
        'footer_corporate_name',
        'corporate_name',
        'farm',
        'city_and_state',
        'cep',
        'cpf_cnpj',
        'dcf',
        'entry_date',
        'today',
        'bank_name',
        'bank_account_number',
        'bank_agency',
        'contract_volume',
        'contract_volume_in_words',
        'price',
        'price_per_ton',
        'estimated_total',
        'estimated_total_in_words',
        'witness',
        'witness_email',
        'witness_cpf',
        'legal_representative',
        'legal_representative_email',
        'legal_representative_cpf',
        'legal_representative2',
        'legal_representative2_email',
        'legal_representative2_cpf',
    ]


def test_header_id():
    filler = ContractFillerService()
    supplier, contract = get_supplier_and_contract_mock()

    contract.id = 5
    contract.entry_date = datetime(2024, 11, 23)
    supplier.corporate_name = 'CBI MADEIRAS LTDA - FAZENDA CORPO DOS PORCOS'

    header_id = filler.get_header_id(supplier, contract)
    assert header_id.strip() == '005_2024_CV_CBI_MADEIRAS_LTDA_FAZENDA_CORPO_DOS_PORCOS'
    assert len(header_id) == 200

    contract.id = 76
    contract.entry_date = datetime(2025, 1, 19)
    supplier.corporate_name = 'JK DOS PALMARES PEREIRA - FAZENDA JURANTES DO ABACAXI'

    header_id = filler.get_header_id(supplier, contract)
    assert header_id.strip() == '076_2025_CV_JK_DOS_PALMARES_PEREIRA_FAZENDA_JURANTES_DO_ABACAXI'
    assert len(header_id) == 200


def test_get_corporate_name():
    filler = ContractFillerService()

    assert filler.get_corporate_name('CBI MADEIRAS LTDA - FAZENDA CORPO DOS PORCOS') == 'CBI MADEIRAS LTDA'
    assert filler.get_corporate_name('JK DOS PALMARES - FAZENDA JURANTES DO ABACAXI') == 'JK DOS PALMARES'
    assert filler.get_corporate_name('CBI MADEIRAS LTDA') == 'CBI MADEIRAS LTDA'


def test_get_farm_name():
    filler = ContractFillerService()

    supplier = MagicMock()

    supplier.corporate_name = 'CBI MADEIRAS LTDA - FAZENDA CORPO DOS PORCOS'
    assert filler.get_farm_name(supplier) == 'Corpo dos Porcos'

    supplier.corporate_name = 'JK DOS PALMARES - FAZENDA JURANTES DO ABACAXI'
    assert filler.get_farm_name(supplier) == 'Jurantes do Abacaxi'

    supplier.corporate_name = 'CBI MADEIRAS LTDA'
    with pytest.raises(ValueError, match=r'Fazenda não encontrada no nome do fornecedor'):
        filler.get_farm_name(supplier)


def test_get_formatted_date():
    filler = ContractFillerService()

    date = datetime(2024, 11, 23)
    formatted_date = filler.get_formatted_date(date)

    assert formatted_date == '23 de novembro de 2024'


def test_get_bank_context():
    filler = ContractFillerService()
    supplier, _ = get_supplier_and_contract_mock()

    bank_context = filler.get_bank_context(supplier)

    assert bank_context['bank_name'] == 'BANCO DO BRASIL'
    assert bank_context['bank_account_number'] == '123456789'
    assert bank_context['bank_agency'] == '1234'


def test_validate_context_missing_variables():
    filler = ContractFillerService()

    supplier, contract = get_supplier_and_contract_mock()
    context = filler.build_context(supplier, contract)

    context.pop('witness_email')

    with pytest.raises(ValueError, match=r'Os seguintes campos do contexto faltam: witness_email'):
        filler.validate_context(context)


def test_get_price_volume_context():
    filler = ContractFillerService()
    _, contract = get_supplier_and_contract_mock()

    contract.contract_volume = 5000
    contract.price = 360

    context = filler.get_price_volume_context(contract)

    assert context['contract_volume'] == 5000
    assert context['contract_volume_in_words'] == 'cinco mil'
    assert context['price'] == 'R$\xa0360,00'
    assert context['price_per_ton'] == 'R$\xa01.531,91'
    assert context['estimated_total'] == 'R$\xa01.800.000,00'
    assert context['estimated_total_in_words'] == 'um milhão e oitocentos mil reais'
