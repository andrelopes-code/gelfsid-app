import pandas as pd
import rich
from django.db import transaction
from django.db.utils import IntegrityError
from rich.console import Console
from rich.prompt import Prompt

from gelfmp.models import CharcoalEntry, Supplier

from .constants import CHARCOAL_ENTRIES_PATH, CHARCOAL_ENTRIES_SHEET_NAME
from .types import Aliases
from .utils import get_best_matches

MINIMUM_SIMILARITY = 95

console = Console()


def datetime_convert(dates):
    date = dates[0]
    if isinstance(date, (int, float)):
        return pd.to_datetime(dates, origin='1899-12-30', unit='D').dt.date
    return pd.to_datetime(dates).dt.date


def get_entries():
    try:
        df = pd.read_excel(CHARCOAL_ENTRIES_PATH, sheet_name=CHARCOAL_ENTRIES_SHEET_NAME)

        # Remove linhas onde o nome do fornecedor está vazio
        df.dropna(subset=['NOME_FORNECEDOR'], inplace=True)

        # Converte as datas de entrada
        df['DATA_ENTRADA'] = datetime_convert(df['DATA_ENTRADA'])

        # Cria a coluna 'FORNECEDOR_E_FAZENDA' com nome do fornecedor e unidade de carbonização
        df.insert(
            1,
            'FORNECEDOR_E_FAZENDA',
            df['NOME_FORNECEDOR'] + ' ' + df['UNIDADE_CARBONIZACAO'].str.split('-').str[0].str.strip(),
        )

        return df

    except Exception as e:
        raise RuntimeError(f'Erro ao carregar o arquivo Excel: {e}')


def process_row(row, supplier):
    try:
        return CharcoalEntry(
            supplier=supplier,
            entry_date=row['DATA_ENTRADA'],
            origin_volume=row['VOL_MDC_ORIGEM'],
            entry_volume=row['VOL_MDC_ENTRADA'],
            moisture=row['UMIDADE'],
            density=row['DENSIDADE_BU'],
            fines=row['FINOS'],
            dcf=row['AUT_DES'],
            gcae=row['GCAE'],
            vehicle_plate=row['PLACA_VEÍCULO'],
            origin_ticket=row['TICKET_ORIGEM'],
        )
    except KeyError as e:
        raise ValueError(f'Campo ausente: {e}')
    except Exception as e:
        raise ValueError(f'Erro ao processar linha: {e}')


def process_data(corporate_name, group):
    try:
        supplier = Supplier.objects.get(corporate_name=corporate_name)
    except Supplier.DoesNotExist:
        raise ValueError(f'Fornecedor {corporate_name} não encontrado no banco de dados')

    entries = []
    for _, row in group.iterrows():
        entry = process_row(row, supplier)
        entries.append(entry)

    if entries:
        try:
            with transaction.atomic():
                CharcoalEntry.objects.bulk_create(entries)
        except IntegrityError as e:
            rich.print(f'[red]{e} -> [blue]{group["NOME_FORNECEDOR"].iloc[0]}[/blue]')


def collect():
    suppliers_names = list(Supplier.objects.values_list('corporate_name', flat=True))
    if not suppliers_names:
        raise ValueError('Não existem fornecedores no banco de dados')

    aliases = Aliases('charcoal.alias.json')
    entries = get_entries()

    for entry_supplier_name, group in entries.groupby('FORNECEDOR_E_FAZENDA'):
        if entry_supplier_name in aliases:
            process_data(aliases.get(entry_supplier_name), group)
            continue

        # Encontra as melhores correspondências de fornecedor
        best_matches = get_best_matches(entry_supplier_name, suppliers_names)

        # Pega a melhor correspondência (a primeira)
        similarity, supplier_name = best_matches[0]

        if similarity >= MINIMUM_SIMILARITY:
            process_data(supplier_name, group)
            continue

        console.print(f'\n[bold red]FORNECEDOR NÃO ENCONTRADO:[/bold red] {entry_supplier_name}')
        console.print('\n[bold yellow]Escolha uma das opções abaixo ou pressione Enter para pular.[/bold yellow]\n')

        for i, (similarity, name) in enumerate(best_matches, start=1):
            console.print(f'[cyan]{i}.[/cyan] {name} [dim](Similaridade: {similarity:.2f}%)[/dim]')

        option = Prompt.ask('\n[green]Digite o número da opção escolhida[/green]', default='').strip()

        if option.isdigit():
            option = int(option) - 1
            if 0 <= option < len(best_matches):
                supplier_name = best_matches[option][1]
                aliases.add(entry_supplier_name, supplier_name)
                process_data(supplier_name, group)
                console.print(
                    '[bold green]Fornecedor mapeado com sucesso![/bold green]'
                    f'{entry_supplier_name} -> {supplier_name}\n'
                )
            else:
                console.print('[bold yellow]Opção inválida. Nenhuma ação foi realizada.[/bold yellow]\n')
        else:
            console.print('[bold yellow]Nenhuma correspondência selecionada. Continuando...[/bold yellow]\n')
