from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import redirect, render

from gelfcore.router import Router
from gelfmp.charts import charts, forms
from gelfmp.models import Supplier

router = Router()


@router(name='index')
def index(request: HttpRequest):
    return render(request, 'index.html')


@router('supplier/<int:id>/', name='supplier_details')
def supplier_details(request: HttpRequest, id):
    supplier = Supplier.objects.filter(id=id).first()
    if not supplier:
        return redirect('index')

    context = {
        'supplier': supplier,
    }

    return render(request, 'supplier/index.html', context=context)


@router('supplier/<int:id>/stats', name='charcoal_supplier_stats')
def supplier_stats(request: HttpRequest, id):
    supplier = Supplier.objects.filter(id=id).first()
    if not supplier or not supplier.is_charcoal_supplier():
        return redirect('index')

    context = {
        'supplier': supplier,
        'charts': [
            {
                'id': 'supplier_charcoal_entries',
                'form_id': 'supplier_stats_form',
                'data': charts.supplier_charcoal_entries(supplier=id, html=True),
                'form': forms.CharcoalSupplierEntriesChartForm(supplier_id=id),
            },
            {
                'id': 'supplier_iqfs_last_3_months',
                'data': charts.supplier_iqfs_last_3_months(supplier_id=id, html=True),
            },
            {
                'id': 'supplier_average_moisture_and_fines',
                'form_id': 'supplier_stats_form',
                'data': charts.supplier_average_moisture_and_fines(supplier=id, html=True),
            },
            {
                'id': 'supplier_average_density',
                'form_id': 'supplier_stats_form',
                'data': charts.supplier_average_density(supplier=id, html=True),
            },
        ],
    }

    return render(request, 'supplier/stats/index.html', context=context)


@router('supplier/htmx/search/', name='supplier_search_htmx')
def supplier_search(request: HttpRequest):
    suppliers = []

    if query := request.GET.get('q'):
        suppliers = Supplier.objects.filter(
            Q(corporate_name__icontains=query) | Q(city__name__icontains=query) | Q(cpf_cnpj__icontains=query),
        )

    return render(request, 'htmx/supplier_search/results.html', {'suppliers': suppliers})


@router('dashboard/charcoal/', name='charcoal_dashboard')
def dashboard(request: HttpRequest):
    context = {
        'charts': [
            {
                'id': 'charcoal_entries',
                'form_id': 'charcoal_entries_form',
                'data': charts.charcoal_entries(html=True),
                'form': forms.CharcoalEntriesChartForm(),
            },
            {
                'id': 'average_density',
                'data': charts.average_density(html=True),
            },
            {
                'id': 'average_moisture_and_fines',
                'data': charts.average_moisture_and_fines(html=True),
            },
        ],
    }

    return render(request, 'dashboard/charcoal.html', context=context)
