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
    return render(
        request,
        'tasks/calculate_iqf.html',
        {
            'form': CalculateIQFForm(),
        },
    )


@staff_member_required
@router('htmx/iqf/', name='calculate_iqf_htmx')
def calculate_iqf_htmx(request: HttpRequest):
    form = CalculateIQFForm(request.POST)

    if request.method == 'POST' and form.is_valid():
        try:
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            processed_suppliers = calculate_suppliers_iqf(month, year)

            return render(request, 'htmx/iqf/results.html', {'processed_suppliers': processed_suppliers})

        except Exception as e:
            return render(request, 'htmx/iqf/results.html', {'processed_suppliers': [str(e)]})
