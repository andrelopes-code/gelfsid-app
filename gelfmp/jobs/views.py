from io import BytesIO

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from gelfcore.router import Router
from gelfmp.models.charcoal_contract import CharcoalContract
from gelfmp.services.contract_filler import contract_filler
from gelfmp.services.iqf_calculator import calculate_suppliers_iqf

from .forms import CalculateIQFForm, DynamicContractForm

router = Router('jobs/')


@staff_member_required
@router('iqf/')
def calculate_iqf(request: HttpRequest):
    return render(
        request,
        'jobs/calculate_iqf.html',
        {
            'form': CalculateIQFForm(),
        },
    )


@staff_member_required
@router('htmx/iqf/')
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


@router('contract/<int:id>/generate/')
def generate_charcoal_contract(request: HttpRequest, id):
    contract = get_object_or_404(CharcoalContract, pk=id)
    supplier = contract.supplier

    contract_context = contract_filler.build_context(supplier, contract)

    if request.method == 'POST':
        try:
            output = BytesIO()

            contract_filler.fill_contract(supplier, contract, output, contract_context | request.POST.dict())
            filename = f'{contract_context["header_id"].strip()}.docx'

            output.seek(0)

            return HttpResponse(
                output,
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                headers={'Content-Disposition': f'attachment; filename={filename}'},
            )

        except Exception as e:
            return render(request, 'components/errors/error.html', {'error': str(e)})

    return render(
        request,
        'jobs/generate_charcoal_contract.html',
        {
            'supplier': supplier,
            'contract': contract,
            'form': DynamicContractForm(contract_context=contract_context),
        },
    )