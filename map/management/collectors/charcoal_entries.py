import pandas as pd
import rich

from map.models import Supplier

from .constants import CHARCOAL_ENTRIES_PATH, CHARCOAL_ENTRIES_SHEET_NAME
from .utils import get_best_matches

MIN_SIMILARITY = 95


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
        best_matches = get_best_matches(name, suppliers_names)
        if not best_matches:
            raise ValueError()

        similarity = best_matches[0][0]
        corporate_name = best_matches[0][1]

        if similarity >= MIN_SIMILARITY:
            rich.print(
                f'nome planilha docs: {corporate_name}\n'
                f'nome entrada carvão: {name}\n'
                f'similaridade: [{similarity:.2f}]\n'
                f'total vol. entrada: {group["VOL_MDC_ENTRADA"].sum():.2f}\n'
                f'data de entrada: {group["DATA_ENTRADA"].min().strftime("%d/%m/%Y")}\n'
                f'volume finos fora: {group.loc[group["FINOS"] >= 10, "VOL_MDC_ENTRADA"].sum():.2f}\n'
                f'volume umidade fora: {group.loc[group["UMIDADE"] >= 7, "VOL_MDC_ENTRADA"].sum():.2f}\n'
                f'volume densidade fora: {group.loc[group["DENSIDADE_BU"] < 210, "VOL_MDC_ENTRADA"].sum():.2f}\n'
            )
        else:
            rich.print(f'[red][NOT FOUND] {name}[/red]')

            for i in range(len(best_matches)):
                rich.print(f'{i} - {best_matches[i][0]:.2f} -> [yellow]{best_matches[i][1]}[/yellow]')

            option = input('O nome corresponde a alguma dessas opções? [digite o número ou enter para passar]: ')
            if option.isdigit() and int(option) < len(best_matches):
                print(f'>>> {best_matches[int(option)]}')
