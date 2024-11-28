from django.http import JsonResponse

from map.models import Supplier


def get_suppliers(request):
    suppliers = Supplier.objects.select_related('city', 'state').all()

    data = [
        {
            'id': supplier.id,
            'corporate_name': supplier.corporate_name,
            'cpf_cnpj': supplier.cpf_cnpj,
            'material_type': supplier.material_type,
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
            'documents': [
                {
                    'id': document.id,
                    'name': document.name,
                    'type': document.type,
                    'filepath': document.filepath,
                    'validity': document.validity,
                    'status': document.status,
                }
                for document in supplier.get_documents()
            ],
        }
        for supplier in suppliers
    ]

    return JsonResponse(data, safe=False)


def get_materials(request):
    materials = Supplier.objects.values_list('material_type', flat=True)
    materials_list = list(set(list(materials)))
    materials_list.sort()

    return JsonResponse(materials_list, safe=False)
