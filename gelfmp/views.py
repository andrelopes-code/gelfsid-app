from django.db.models import Q, Sum
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.utils.timezone import now

from gelfcore.router import Router
from gelfmp.charts import charts, forms
from gelfmp.models import CharcoalMonthlyPlan, Supplier
from gelfmp.models.charcoal_entry import CharcoalEntry
from gelfmp.models.choices import SupplierType
from gelfmp.services.cnpj_info import CNPJInfoService

router = Router()
cnpj_service = CNPJInfoService()


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


@router('supplier/<int:id>/cnpj', name='supplier_cnpj_info')
def supplier_cnpj_info(request: HttpRequest, id):
    supplier = Supplier.objects.filter(id=id).first()
    if not supplier:
        return redirect('index')

    cnpj_data = cnpj_service.fetch(supplier.cpf_cnpj)

    context = {
        'supplier': supplier,
        'cnpj_info': cnpj_data,
    }

    return render(request, 'supplier/cnpj/index.html', context=context)


@router('supplier/htmx/search/', name='supplier_search_htmx')
def supplier_search(request: HttpRequest):
    suppliers = []

    if query := request.GET.get('q'):
        # Busca por nome, cidade ou CPF/CNPJ
        suppliers = Supplier.objects.filter(
            Q(corporate_name__icontains=query) | Q(city__name__icontains=query) | Q(cpf_cnpj__icontains=query),
        )

    return render(request, 'htmx/supplier_search/results.html', {'suppliers': suppliers})


@router('dashboard/charcoal/', name='charcoal_dashboard')
def charcoal_dashboard(request: HttpRequest):
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


@router('dashboard/schedule/', name='charcoal_schedule')
def charcoal_schedule(request: HttpRequest):
    year = now().year

    # Obtem as programações do ano informado.
    plans = CharcoalMonthlyPlan.objects.filter(year=year).order_by(
        'supplier__supplier_type',
        'supplier__corporate_name',
        'month',
    )

    supplier_types = {supplier_type: display for supplier_type, display in SupplierType.choices}
    grouped_data = {supplier_type: {'planned': ['-'] * 12, 'realized': ['-'] * 12} for supplier_type in supplier_types}

    for plan in plans:
        month_index = plan.month - 1
        supplier_type = plan.supplier.supplier_type

        if grouped_data[supplier_type]['planned'][month_index] == '-':
            grouped_data[supplier_type]['planned'][month_index] = 0

        grouped_data[supplier_type]['planned'][month_index] += plan.planned_volume

    charcoal_entries = (
        CharcoalEntry.objects.filter(entry_date__year=year)
        .values('supplier__supplier_type', 'entry_date__month')
        .annotate(realized_volume=Sum('entry_volume'))
    )

    for entry in charcoal_entries:
        supplier_type = entry['supplier__supplier_type']
        month_index = entry['entry_date__month'] - 1
        realized_volume = entry['realized_volume']

        grouped_data[supplier_type]['realized'][month_index] = round(realized_volume, 2)

    table_data = [
        {'supplier_type': supplier_types[supplier_type], 'planned': data['planned'], 'realized': data['realized']}
        for supplier_type, data in grouped_data.items()
    ]

    month_labels = [
        'Janeiro',
        'Fevereiro',
        'Março',
        'Abril',
        'Maio',
        'Junho',
        'Julho',
        'Agosto',
        'Setembro',
        'Outubro',
        'Novembro',
        'Dezembro',
    ]

    context = {
        'table_data': table_data,
        'year': year,
        'charts': [
            {
                'id': 'charcoal_schedule',
                'data': charts.charcoal_schedule(table_data, year, month_labels, html=True),
            },
        ],
        'months': month_labels,
    }

    return render(request, 'dashboard/charcoal_schedule.html', context=context)
