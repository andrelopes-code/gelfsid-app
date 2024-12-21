from django.contrib.admin.views.decorators import staff_member_required
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from gelfmp.models import City, Supplier


@staff_member_required
def get_cities(request):
    state_id = request.GET.get('state')

    if not state_id:
        return JsonResponse([], safe=False)

    cities = City.objects.filter(state_id=state_id).values('id', 'name')
    return JsonResponse(list(cities), safe=False)


@staff_member_required
def get_supplier(request):
    supplier_id = request.GET.get('id')

    if not supplier_id:
        return JsonResponse({'error': 'supplier ID is required'}, status=400)

    try:
        supplier = get_object_or_404(Supplier, id=supplier_id)
        supplier_data = model_to_dict(supplier)

        if supplier.city:
            supplier_data['city'] = {
                'id': supplier.city.id,
                'name': supplier.city.name,
            }

        return JsonResponse(supplier_data)

    except Supplier.DoesNotExist:
        return JsonResponse({'error': 'supplier not found'}, status=404)
