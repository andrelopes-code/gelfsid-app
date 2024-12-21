from django import forms

from gelfmp.models import Supplier


class CharcoalEntriesChartForm(forms.Form):
    group_by = forms.ChoiceField(
        choices=[('day', 'Diária'), ('week', 'Semanal'), ('month', 'Mensal')],
        label='Modo de Exibição',
        required=False,
    )

    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.filter(material_type='Carvão Vegetal').all(),
        label='Fornecedor',
        required=False,
        empty_label='Todos',
    )

    start_date = forms.DateField(
        label='Data de Início',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
    )

    end_date = forms.DateField(
        label='Data de Fim',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
    )


class CharcoalSupplierEntriesChartForm(forms.Form):
    group_by = forms.ChoiceField(
        choices=[('day', 'Diária'), ('week', 'Semanal'), ('month', 'Mensal')],
        label='Modo de Exibição',
        required=False,
    )

    supplier = forms.CharField(widget=forms.HiddenInput, required=True)

    start_date = forms.DateField(
        label='Data de Início',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
    )

    end_date = forms.DateField(
        label='Data de Fim',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
    )

    def __init__(self, *args, supplier_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        if supplier_id:
            self.fields['supplier'].initial = supplier_id
