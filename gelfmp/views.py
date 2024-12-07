from django.http import HttpRequest
from django.shortcuts import redirect, render

from gelfmp.charts import charts, forms
from gelfmp.models import Supplier


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


def supplier_details(request: HttpRequest, id):
    supplier = Supplier.objects.filter(id=id).first()
    if not supplier:
        return redirect('index')

    context = {
        'supplier': supplier,
    }

    return render(request, 'details/index.html', context=context)
