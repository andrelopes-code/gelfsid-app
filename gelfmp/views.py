from django.db.models import Q, Sum
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.utils.timezone import now
from httpx import ReadTimeout

from gelfcore.router import Router
from gelfmp.charts import charts, forms
from gelfmp.models import CharcoalEntry, CharcoalMonthlyPlan, Supplier, SupplierType
from gelfmp.services.cnpj_info import CNPJInfoService

router = Router()
cnpj_service = CNPJInfoService()


@router()
def index(request: HttpRequest):
    return render(request, 'index.html')


@router('supplier/<int:id>/')
def supplier_details(request: HttpRequest, id):
    supplier = Supplier.objects.filter(id=id).first()
    if not supplier:
        return redirect('index')

    context = {
        'supplier': supplier,
    }

    return render(request, 'supplier/index.html', context=context)


@router('supplier/<int:id>/stats')
def charcoal_supplier_stats(request: HttpRequest, id):
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


@router('supplier/<int:id>/cnpj')
def supplier_cnpj_info(request: HttpRequest, id):
    supplier = Supplier.objects.filter(id=id).first()
    if not supplier:
        return redirect('index')

    try:
        cnpj_data = cnpj_service.fetch(supplier.cpf_cnpj)

        # Atualizar os dados de endereço do fornecedor
        # com os dados atualizados vindo da consulta do CNPJ.
        supplier.cep = cnpj_data['address']['zip']
        supplier.address = ', '.join([
            cnpj_data['address']['street'],
            cnpj_data['address']['number'],
            cnpj_data['address']['district'],
        ])

        if complement := cnpj_data['address']['details']:
            supplier.address += f', {complement}'

        supplier.save()

    except (ValueError, ReadTimeout):
        return render(
            request,
            'components/errors/error.html',
            {'error': 'Não foi possivel carregar os dados do CNPJ no momento, tente novamente mais tarde.'},
        )

    context = {
        'supplier': supplier,
        'cnpj_info': cnpj_data,
    }

    return render(request, 'supplier/cnpj/index.html', context=context)


@router('supplier/htmx/search/')
def supplier_search_htmx(request: HttpRequest):
    suppliers = []

    if q := request.GET.get('q'):
        terms = q.strip().split()

        query = Q()
        for term in terms:
            query &= Q(corporate_name__icontains=term)

        suppliers = Supplier.objects.filter(query)

    return render(request, 'htmx/supplier_search/results.html', {'suppliers': suppliers})


@router('dashboard/charcoal/')
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


@router('dashboard/schedule/')
def charcoal_schedule(request: HttpRequest):
    current_year = now().year

    year_plans = CharcoalMonthlyPlan.objects.filter(year=current_year).order_by(
        'supplier__supplier_type',
        'supplier__corporate_name',
        'month',
    )

    supplier_types = {supplier_type: display for supplier_type, display in SupplierType.choices}
    grouped_data = {supplier_type: {'planned': ['-'] * 12, 'realized': ['-'] * 12} for supplier_type in supplier_types}

    for plan in year_plans:
        month_index = plan.month - 1
        supplier_type = plan.supplier.supplier_type

        if grouped_data[supplier_type]['planned'][month_index] == '-':
            grouped_data[supplier_type]['planned'][month_index] = 0

        grouped_data[supplier_type]['planned'][month_index] += plan.planned_volume

    charcoal_entries = (
        CharcoalEntry.objects.filter(entry_date__year=current_year)
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
        'year': current_year,
        'charts': [
            {
                'id': 'charcoal_schedule',
                'data': charts.charcoal_schedule(table_data, current_year, month_labels, html=True),
            },
        ],
        'months': month_labels,
    }

    return render(request, 'dashboard/charcoal_schedule.html', context=context)
