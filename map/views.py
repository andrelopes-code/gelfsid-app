from django.http import HttpRequest
from django.shortcuts import render

from map.charts import charts, forms


def index(request: HttpRequest):
    return render(request, 'index.html')


def dashboard(request: HttpRequest):
    context = {
        'charcoal_entries': charts.charcoal_entries(html=True),
        'charcoal_entries_form': forms.CharcoalEntriesChartForm(),
        'density': charts.density(html=True),
        'moisture_and_fines': charts.moisture_and_fines(html=True),
    }

    return render(request, 'dashboard/index.html', context=context)
