from django import forms

from gelfmp.models import Supplier


class CharcoalEntriesChartForm(forms.Form):
    group_by = forms.ChoiceField(
        choices=[('day', 'Diária'), ('week', 'Semanal'), ('month', 'Mensal')],
        label='Modo de Exibição',
        required=False,
    )

    months = forms.IntegerField(label='Meses', initial=3, required=False, min_value=1, max_value=24)

    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.filter(material_type='Carvão Vegetal').all(),
        label='Fornecedor',
        required=False,
        empty_label='Todos',
    )


class CharcoalSupplierEntriesChartForm(forms.Form):
    group_by = forms.ChoiceField(
        choices=[('day', 'Diária'), ('week', 'Semanal'), ('month', 'Mensal')],
        label='Modo de Exibição',
        required=False,
    )

    months = forms.IntegerField(label='Meses', initial=3, required=False, min_value=1, max_value=24)
    supplier = forms.CharField(widget=forms.HiddenInput, required=True)

    def __init__(self, *args, supplier_id, **kwargs):
        super().__init__(*args, **kwargs)

        if supplier_id:
            self.fields['supplier'].initial = supplier_id
