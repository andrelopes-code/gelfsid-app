from django import forms
from django.utils import timezone

from gelfmp import models


class CalculateIQFForm(forms.Form):
    current_month = timezone.now().month
    current_year = timezone.now().year
    last_month = 12 if current_month == 1 else current_month - 1

    month = forms.ChoiceField(choices=models.MonthType.choices, label='Mês de Referência', initial=last_month)
    year = forms.ChoiceField(choices=models.year_choices(), label='Ano de Referência', initial=current_year)
