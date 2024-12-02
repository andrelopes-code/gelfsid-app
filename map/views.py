from django.http import HttpRequest
from django.shortcuts import render

from map import charts, forms


def index(request: HttpRequest):
    return render(request, 'index.html')


def dashboard(request: HttpRequest):
    context = {
        'charcoal_entries': charts.charcoal_entries(html=True),
        'charcoal_entries_form': forms.CharcoalEntriesChartForm(),
        'density_by_day': charts.density_by_day(html=True),
        'moisture_and_fines_by_day': charts.moisture_and_fines_by_day(html=True),
    }

    return render(request, 'dashboard/index.html', context=context)
