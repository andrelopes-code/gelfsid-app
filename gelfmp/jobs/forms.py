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
    }

    def __init__(self, *args, **kwargs):
        contract_context = kwargs.pop('contract_context', None)
        super().__init__(*args, **kwargs)

        if contract_context:
            for field, value in contract_context.items():
                if field not in self.EXCLUDED_FIELDS:
                    self.fields[field] = forms.CharField(
                        initial=value,
                        label=field.upper(),
                        strip=False,
                        required=False,
                    )
