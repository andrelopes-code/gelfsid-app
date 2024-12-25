from unittest.mock import MagicMock

import pandas as pd
import pytest

from gelfmp.models.choices import SupplierType
from gelfmp.services.iqf_calculator import calculate_iqf, calculate_suppliers_iqf, calculate_valid_percentage


def test_calculate_percentage():
    assert calculate_valid_percentage(0, 200) == 100.0
    assert calculate_valid_percentage(50, 100) == 50.0
    assert calculate_valid_percentage(200, 200) == 0.0
    assert calculate_valid_percentage(450, 300) == 0.0


def test_calculate_iqf():
    entries = pd.DataFrame([
        {'entry_volume': 100, 'fines': 8, 'moisture': 9, 'density': 220},
    ])

    iqf_data = calculate_iqf(500, entries)

    assert iqf_data.iqf == 55.0
    assert iqf_data.planned_percentage == 20.0
    assert iqf_data.fines_percentage == 100.0
    assert iqf_data.moisture_percentage == 0.0
    assert iqf_data.density_percentage == 100.0

    entries = pd.DataFrame([
        {'entry_volume': 100, 'fines': 8, 'moisture': 9, 'density': 220},
        {'entry_volume': 200, 'fines': 12, 'moisture': 3, 'density': 205},
        {'entry_volume': 150, 'fines': 10, 'moisture': 7, 'density': 210},
    ])

    iqf_data = calculate_iqf(500, entries)

    assert iqf_data.iqf == 53.1
    assert iqf_data.planned_percentage == 90.0
    assert iqf_data.fines_percentage == 22.22
    assert iqf_data.moisture_percentage == 44.44
    assert iqf_data.density_percentage == 55.56

    entries = pd.DataFrame([
        {'entry_volume': 225, 'fines': 8, 'moisture': 6, 'density': 211},
        {'entry_volume': 400, 'fines': 9, 'moisture': 5, 'density': 240},
        {'entry_volume': 154, 'fines': 3, 'moisture': 2, 'density': 210},
    ])

    iqf_data = calculate_iqf(750, entries)

    assert iqf_data.iqf == 100.0
    assert iqf_data.planned_percentage == 100.0
    assert iqf_data.fines_percentage == 100.0
    assert iqf_data.moisture_percentage == 100.0
    assert iqf_data.density_percentage == 100.0


def test_calculate_suppliers_iqf(mocker):
    mock_entries = MagicMock()
    mock_entries.exists.return_value = True
    mock_entries.values.return_value = [
        {'supplier_id': 1, 'entry_volume': 100, 'fines': 8, 'moisture': 6, 'density': 220},
        {'supplier_id': 1, 'entry_volume': 200, 'fines': 12, 'moisture': 9, 'density': 205},
    ]

    mock_supplier = MagicMock()
    mock_supplier.corporate_name = 'Fornecedor Teste'
    mock_supplier.supplier_type = SupplierType.THIRD_PARTY

    mocker.patch('gelfmp.models.CharcoalEntry.objects.filter', return_value=mock_entries)
    mocker.patch('gelfmp.models.Supplier.objects.get', return_value=mock_supplier)
    mocker.patch('gelfmp.models.CharcoalMonthlyPlan.objects.get', return_value=MagicMock(planned_volume=500))
    mocker.patch('gelfmp.models.CharcoalIQF.objects.filter', return_value=MagicMock(first=MagicMock(return_value=None)))

    def custom_update_or_create(*_, **kwargs):
        supplier = kwargs['supplier']
        month = kwargs['month']
        year = kwargs['year']
        data = kwargs['defaults']

        assert supplier.corporate_name == 'Fornecedor Teste'
        assert supplier.supplier_type == SupplierType.THIRD_PARTY
        assert month == 12
        assert year == 2024

        assert data['iqf'] == 40.0
        assert data['planned_percentage'] == 60.0
        assert data['fines_percentage'] == 33.33
        assert data['moisture_percentage'] == 33.33
        assert data['density_percentage'] == 33.33

    mocker.patch('gelfmp.models.CharcoalIQF.objects.update_or_create', side_effect=custom_update_or_create)

    processed_suppliers = calculate_suppliers_iqf(12, 2024)

    assert len(processed_suppliers) == 1
    assert 'IQF CALCULADO' in processed_suppliers[0]


def test_calculate_suppliers_iqf_no_entries(mocker):
    mock_entries = MagicMock()
    mock_entries.exists.return_value = False

    mocker.patch('gelfmp.models.CharcoalEntry.objects.filter', return_value=mock_entries)

    with pytest.raises(ValueError, match=r'Não há entradas de carvão para o mês 12/2024.'):
        calculate_suppliers_iqf(12, 2024)
