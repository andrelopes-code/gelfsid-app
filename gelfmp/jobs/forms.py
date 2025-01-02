from django import forms

from gelfmp import models
from gelfmp.utils import dtutils


class CalculateIQFForm(forms.Form):
    month = forms.ChoiceField(
        choices=models.Month.choices,
        label='Mês de Referência',
        initial=dtutils.last_month(),
    )

    year = forms.ChoiceField(
        choices=models.year_choices(),
        label='Ano  de Referência',
        initial=dtutils.current_year(),
    )


class DynamicContractForm(forms.Form):
    EXCLUDED_FIELDS = {
        'header_id',
        'entry_date',
        'dcf',
        'today',
        'contract_volume',
        'contract_volume_in_words',
        'price',
        'price_per_ton',
        'estimated_total',
        'estimated_total_in_words',
    }

    TRANSLATED_FIELDS = {
        'footer_corporate_name': 'Nome no Rodapé',
        'corporate_name': 'Razão Social',
        'farm': 'Fazenda',
        'city_and_state': 'Cidade e Estado',
        'cep': 'CEP',
        'cpf_cnpj': 'CPF/CNPJ',
        'bank_name': 'Banco',
        'bank_account': 'Conta Corrente',
        'bank_agency': 'Agência',
        'witness': 'Testemunha',
        'witness_email': 'E-mail da Testemunha',
        'witness_cpf': 'CPF da Testemunha',
        'legal_representative': 'Representante Legal 01',
        'legal_representative_email': 'E-mail do Representante Legal 01',
        'legal_representative_cpf': 'CPF do Representante Legal 01',
        'legal_representative2': 'Representante Legal 02',
        'legal_representative2_email': 'E-mail do Representante Legal 02',
        'legal_representative2_cpf': 'CPF do Representante Legal 02',
    }

    def __init__(self, *args, **kwargs):
        contract_context = kwargs.pop('contract_context', None)
        super().__init__(*args, **kwargs)

        if contract_context:
            for field, value in contract_context.items():
                if field not in self.EXCLUDED_FIELDS:
                    self.fields[field] = forms.CharField(
                        initial=value,
                        label=self.TRANSLATED_FIELDS.get(field, field),
                        strip=False,
                        required=False,
                    )
