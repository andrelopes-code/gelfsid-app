from django.http import JsonResponse

from map.models import Supplier

HOST_CITY = 'Sete Lagoas, MG'


def get_suppliers(request):
    suppliers = Supplier.objects.select_related('city', 'state').all()

    data = [
        {
            'id': supplier.id,
            'corporate_name': supplier.corporate_name,
            'cpf_cnpj': supplier.cpf_cnpj,
            'material_type': supplier.get_material_type_display(),
            'rating': supplier.rating,
            'state': {
                'abbr': supplier.state.abbr,
                'name': supplier.state.name,
            },
            'city': {
                'id': supplier.city.id,
                'name': supplier.city.name,
            },
            'distance_in_meters': supplier.distance_in_meters,
            # TODO: add documents
            'documents': [],
        }
        for supplier in suppliers
    ]

    return JsonResponse(data, safe=False)
