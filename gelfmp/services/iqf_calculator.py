import pandas as pd

from gelfcore.logger import log
from gelfmp.models import CharcoalEntry, CharcoalIQF, CharcoalMonthlyPlan, MaterialType, Supplier

MOISTURE_MAX = 7
FINES_MAX = 10
MIN_DENSITY = 210


def calculate_percentage(value, total):
    """
    Calcula o percentual de um valor em relação ao total.
    """
    valid = total - value
    return (valid / total) * 100


def calculate_invalid_volume_percentage(entries: pd.DataFrame, total_volume, max_fines, max_moisture, min_density):
    """
    Calcula o percentual de volume inválido para finos, umidade e densidade.
    """
    fines_above_max = entries[entries['fines'] >= max_fines]
    moisture_above_max = entries[entries['moisture'] >= max_moisture]
    density_below_min = entries[entries['density'] < min_density]

    volume_fines_above_max = fines_above_max['entry_volume'].sum()
    volume_moisture_above_max = moisture_above_max['entry_volume'].sum()
    volume_density_below_min = density_below_min['entry_volume'].sum()

    fines_percentage = calculate_percentage(volume_fines_above_max, total_volume)
    moisture_percentage = calculate_percentage(volume_moisture_above_max, total_volume)
    density_percentage = calculate_percentage(volume_density_below_min, total_volume)

    return fines_percentage, moisture_percentage, density_percentage


def calculate_iqf(programmed_volume: float, entries: pd.DataFrame):
    """
    Calcula o IQF baseado no volume programado e nas entradas.
    """
    total_volume = entries['entry_volume'].sum()
    programmed_percentage = min(total_volume / programmed_volume * 100, 100)

    fines_percentage, moisture_percentage, density_percentage = calculate_invalid_volume_percentage(
        entries,
        total_volume,
        FINES_MAX,
        MOISTURE_MAX,
        MIN_DENSITY,
    )

    iqf = (programmed_percentage + fines_percentage + moisture_percentage + density_percentage) / 4

    if iqf > 100:
        return f'O IQF não pode ser maior que 100: {iqf:.2f}'

    return (
        round(iqf, 2),
        round(programmed_percentage, 2),
        round(fines_percentage, 2),
        round(moisture_percentage, 2),
        round(density_percentage, 2),
    )


def calculate_suppliers_iqf(month, year):
    """
    Função principal para calcular IQF por fornecedor e mês.
    """
    entries = CharcoalEntry.objects.filter(
        entry_date__month=month,
        entry_date__year=year,
        supplier__material_type=MaterialType.CHARCOAL,
    )

    if not entries.exists():
        raise ValueError(f'Não há entradas de carvão para o mês {month}/{year}.')

    entries_df = pd.DataFrame(entries.values())
    processed_suppliers = []

    for _, supplier_entries in entries_df.groupby('supplier_id'):
        supplier_id = supplier_entries.iloc[0]['supplier_id']

        try:
            supplier = Supplier.objects.get(id=supplier_id)
            plan = CharcoalMonthlyPlan.objects.get(supplier=supplier, month=month, year=year)

        except CharcoalMonthlyPlan.DoesNotExist:
            log.warning(
                f'Não existe uma programação de carvão para o fornecedor '
                f'{supplier} ({supplier_id}) no mês {month}/{year}.'
            )
            continue

        except Supplier.DoesNotExist:
            log.warning(f'Fornecedor com ID {supplier_id} não encontrado.')
            continue

        iqf, programmed_percentage, fines_percentage, moisture_percentage, density_percentage = calculate_iqf(
            plan.programmed_volume, supplier_entries
        )

        existing_iqf = CharcoalIQF.objects.filter(supplier=supplier, month=month, year=year).first()
        if existing_iqf:
            log.warning(f'O IQF já foi calculado para o fornecedor {supplier} no mês {month}/{year}.')
            continue

        try:
            CharcoalIQF.objects.create(
                supplier=supplier,
                iqf=iqf,
                month=month,
                year=year,
                programmed_percentage=programmed_percentage,
                fines_percentage=fines_percentage,
                moisture_percentage=moisture_percentage,
                density_percentage=density_percentage,
            )

            processed_suppliers.append(f'IQF CALCULADO PARA {supplier}: {iqf}')

        except Exception as e:
            log.error(f'Erro ao salvar IQF para o fornecedor {supplier.name}: {e}')
            raise Exception(f'Erro ao salvar IQF para o fornecedor {supplier.name}')

    return processed_suppliers
