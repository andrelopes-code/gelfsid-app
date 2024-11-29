import pandas as pd
import rich

from map.models import Supplier

from .constants import IQF_PATH, IQF_SHEET_NAME
from .utils import get_best_matches, normalize_and_compare


def get_iqf_data():
    df = pd.read_excel(IQF_PATH, usecols='B:L', skiprows=1, sheet_name=IQF_SHEET_NAME)

    # Remove linhas vazias ou invalidas
    invalid_rows = df.isnull().all(axis=1) | (df['FORNECEDOR'] == '')
    stop_index = invalid_rows.idxmax() if invalid_rows.any() else len(df)
    df = df[:stop_index]

    return df


def collect(threshold=95):
    iqf_data = get_iqf_data()
    corporate_names = list(Supplier.objects.values_list('corporate_name', flat=True))

    for _, row in iqf_data.iterrows():
        iqf_corporate_name = row['FORNECEDOR']

        for corporate_name in corporate_names:
            similarity = normalize_and_compare(iqf_corporate_name, corporate_name)
            if similarity >= threshold:
                rich.print(f'{iqf_corporate_name}\n{corporate_name}\n{similarity}')
                break

        else:
            rich.print(f'[red][NOT FOUND] {iqf_corporate_name}[/red]')
            rich.print(
                get_best_matches(
                    iqf_corporate_name,
                    corporate_names,
                )
            )
            input()
