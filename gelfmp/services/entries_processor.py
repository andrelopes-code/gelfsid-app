import pandas as pd
from django.db import transaction
from django.db.utils import IntegrityError

from gelfmp.management.commands.collectors.utils import get_best_matches
from gelfmp.models import CharcoalEntry, Supplier
from gelfmp.models.alias import Alias
from gelfmp.models.dcf import DCF

CHARCOAL_ENTRIES_SHEET_NAME = 'Entrada de Carvão'
MINIMUM_SIMILARITY = 95


class EntriesProcessor:
    """Classe para processar arquivos excel de entrada de carvão"""

    def __init__(self):
        self.suppliers_not_found = []
        self.entries = []

        self.aliases = {
            alias['alias']: alias['supplier__corporate_name']
            for alias in Alias.objects.values('alias', 'supplier__corporate_name')
        }

        self.suppliers_names = list(Supplier.objects.values_list('corporate_name', flat=True))

    def process(self, entries_file_list):
        if not self.suppliers_names:
            raise ValueError('Não existem fornecedores no banco de dados.')

        for entries_file in entries_file_list:
            entries = self._get_entries_df(entries_file)

            for supplier_name, group in entries.groupby('FORNECEDOR_E_FAZENDA'):
                if supplier_name in self.aliases:
                    self._process_entries(self.aliases.get(supplier_name), group)
                    continue

                best_matches = get_best_matches(supplier_name, self.suppliers_names)
                similarity, best_match = best_matches[0]

                if similarity >= MINIMUM_SIMILARITY:
                    self._process_entries(best_match, group)
                    continue

                # Caso não seja possível identificar o fornecedor
                # armazena na lista de fornecedores não encontrados.
                self.suppliers_not_found.append(supplier_name)

        if self.suppliers_not_found:
            raise ValueError(
                'Os seguintes fornecedores não foram encontrados no banco de dados: '
                f'{", ".join(self.suppliers_not_found)}. '
                'Caso existam no sistema, porém com outro nome, adicione o nome acima '
                'como um alias para o fornecedor desejado em Fornecedor -> Aliases.'
            )

        self._save_entries()

    def _get_entries_df(self, entries_file):
        try:
            df = pd.read_excel(entries_file, sheet_name=CHARCOAL_ENTRIES_SHEET_NAME)

            # Remove linhas onde o nome do fornecedor está vazio
            df.dropna(subset=['NOME_FORNECEDOR'], inplace=True)

            # Converte as datas de entrada
            df['DATA_ENTRADA'] = self._datetime_convert(df['DATA_ENTRADA'])

            # Cria a coluna 'FORNECEDOR_E_FAZENDA' com nome do
            # fornecedor e unidade de carbonização
            df.insert(
                1,
                'FORNECEDOR_E_FAZENDA',
                df['NOME_FORNECEDOR'] + ' ' + df['UNIDADE_CARBONIZACAO'].str.split('-').str[0].str.strip(),
            )

            return df

        except Exception as e:
            raise RuntimeError(f'Erro ao carregar o arquivo Excel: {e}')

    def _process_entries(self, corporate_name, group):
        supplier = Supplier.objects.filter(corporate_name=corporate_name).first()
        if not supplier:
            raise ValueError(f'Fornecedor {corporate_name} não encontrado no banco de dados')

        for _, row in group.iterrows():
            self.entries.append(self._process_row(row, supplier))

    def _process_row(self, row, supplier):
        try:
            dcf, _ = DCF.objects.get_or_create(process_number=row['AUT_DES'], defaults={'supplier': supplier})

            return CharcoalEntry(
                supplier=supplier,
                entry_date=row['DATA_ENTRADA'],
                origin_volume=row['VOL_MDC_ORIGEM'],
                entry_volume=row['VOL_MDC_ENTRADA'],
                moisture=row['UMIDADE'],
                density=row['DENSIDADE_BU'],
                fines=row['FINOS'],
                gcae=row['GCAE'],
                vehicle_plate=row['PLACA_VEÍCULO'],
                origin_ticket=row['TICKET_ORIGEM'],
                dcf=dcf,
            )

        except KeyError as e:
            raise ValueError(f'Campo ausente: {e}')

        except Exception as e:
            raise ValueError(f'Erro ao processar linha: {e}')

    def _save_entries(self):
        if self.entries:
            try:
                with transaction.atomic():
                    CharcoalEntry.objects.bulk_create(self.entries)

            except IntegrityError as e:
                if 'ticket' not in str(e).lower():
                    raise

    def _datetime_convert(self, dates):
        date = dates[0]

        if isinstance(date, (int, float)):
            return pd.to_datetime(dates, origin='1899-12-30', unit='D').dt.date

        return pd.to_datetime(dates).dt.date
