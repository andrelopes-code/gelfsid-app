from django.http import HttpRequest
from django.shortcuts import render

from map import charts


def index(request: HttpRequest):
    return render(request, 'index.html')


def dashboard(request: HttpRequest):
    context = {
        'daily_entries_chart': charts.charcoal_entries(),
        'density_by_day': charts.density_by_day(),
        'moisture_and_fines_by_day': charts.moisture_and_fines_by_day(),
    }

    return render(request, 'dashboard/index.html', context=context)
