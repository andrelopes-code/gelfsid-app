from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render

from gelfcore.router import Router
from gelfmp.models import Supplier

router = Router('htmx/')


@router('supplier/search/', name='supplier_search')
def supplier_search(request: HttpRequest):
    suppliers = []

    if query := request.GET.get('q'):
        suppliers = Supplier.objects.filter(
            Q(corporate_name__icontains=query) | Q(city__name__icontains=query) | Q(cpf_cnpj__icontains=query),
        )

    return render(request, 'htmx/supplier_search_results.html', {'suppliers': suppliers})
