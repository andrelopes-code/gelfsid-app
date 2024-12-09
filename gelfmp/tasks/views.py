from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest
from django.shortcuts import render

from gelfcore.router import Router
from gelfmp.services.iqf_calculator import calculate_suppliers_iqf

from .forms import CalculateIQFForm

router = Router('task/')


@staff_member_required
@router('iqf/', name='calculate_iqf')
def calculate_iqf(request: HttpRequest):
    errors = []
    processed_suppliers = []
    form = CalculateIQFForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        try:
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']

            result = calculate_suppliers_iqf(month, year)
            processed_suppliers = result or ['Nenhum novo IQF de fornecedor foi calculado.']

        except Exception as e:
            errors.append(str(e))

    elif request.method == 'POST':
        errors.append('Formulário inválido.')

    return render(
        request,
        'tasks/calculate_iqf.html',
        {
            'form': form,
            'errors': errors,
            'processed_suppliers': processed_suppliers,
        },
    )
