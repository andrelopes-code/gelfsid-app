from django.contrib.admin.views.decorators import staff_member_required
from django.forms import model_to_dict
from django.http import JsonResponse

from gelfmp.models import City, Supplier


@staff_member_required
def get_cities(request):
    state_id = request.GET.get('state')

    if state_id:
        cities = City.objects.filter(state_id=state_id).values('id', 'name')
        return JsonResponse(list(cities), safe=False)

    return JsonResponse([], safe=False)


@staff_member_required
def get_supplier(request):
    supplier_id = request.GET.get('id')

    if supplier_id:
        supplier = Supplier.objects.filter(id=supplier_id).first()

        if supplier:
            supplier_data = model_to_dict(supplier)

            if supplier.city:
                supplier_data['city'] = {
                    'id': supplier.city.id,
                    'name': supplier.city.name,
                }

            return JsonResponse(supplier_data)
        else:
            return JsonResponse({'error': 'supplier not found'}, status=404)
    else:
        return JsonResponse({'error': 'supplier ID is required'}, status=400)
