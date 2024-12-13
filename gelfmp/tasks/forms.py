from django import forms

from gelfmp import models
from gelfmp.utils import dtutils


class CalculateIQFForm(forms.Form):
    month = forms.ChoiceField(
        choices=models.MonthType.choices,
        label='Mês de Referência',
        initial=dtutils.last_month(),
    )

    year = forms.ChoiceField(
        choices=models.year_choices(),
        label='Ano  de Referência',
        initial=dtutils.current_year(),
    )
