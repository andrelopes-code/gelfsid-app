import pandas as pd
import rich

from map.management.commands._collect.constants import CHARCOAL_ENTRIES_PATH, CHARCOAL_ENTRIES_SHEET_NAME
from map.management.commands._collect.utils import get_best_matches, normalize_and_compare
from map.models import Supplier


def get_entries_data():
    df = pd.read_excel(CHARCOAL_ENTRIES_PATH, sheet_name=CHARCOAL_ENTRIES_SHEET_NAME)

    # Remove as linhas em que o nome do fornecedor está vazio
    df.dropna(subset=['NOME_FORNECEDOR'], inplace=True)

    # Cria uma coluna que contenha o nome do fornecedor junto com a fazenda
    df.insert(
        1,
        'FORNECEDOR_E_FAZENDA',
        df['NOME_FORNECEDOR'] + ' ' + df['UNIDADE_CARBONIZACAO'].str.split('-').str[0].str.strip(),
    )

    return df


def collect():
    suppliers_names = list(Supplier.objects.values_list('corporate_name', flat=True))
    entries_data = get_entries_data()

    for name, group in entries_data.groupby('FORNECEDOR_E_FAZENDA'):
        for corporate_name in suppliers_names:
            similarity = normalize_and_compare(name, corporate_name)
            if similarity >= 95:
                rich.print(
                    f'nome iqf: {name}\n'
                    f'nome doc: {corporate_name}\n'
                    f'similaridade: [{similarity:.2f}]\n'
                    f'total vol. entrada: {group["VOL_MDC_ENTRADA"].sum():.2f}\n'
                    f'data de entrada: {group["DATA_ENTRADA"].min().strftime("%d/%m/%Y")}\n'
                    f'volume finos fora: {group.loc[group["FINOS"] >= 10, "VOL_MDC_ENTRADA"].sum():.2f}\n'
                    f'volume umidade fora: {group.loc[group["UMIDADE"] >= 7, "VOL_MDC_ENTRADA"].sum():.2f}\n'
                    f'volume densidade fora: {group.loc[group["DENSIDADE_BU"] < 210, "VOL_MDC_ENTRADA"].sum():.2f}\n'
                )
                break

        else:
            rich.print(f'[red][NOT FOUND] {name}[/red]')
            rich.print(get_best_matches(name, suppliers_names))
            input()
