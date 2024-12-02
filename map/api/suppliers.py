from django.http import JsonResponse

from map.models import CharcoalEntry, Supplier


def get_suppliers(request):
    try:
        suppliers = Supplier.objects.select_related('city', 'state').all()

        data = []
        for supplier in suppliers:
            recent_entries = list(CharcoalEntry.objects.filter(supplier=supplier).order_by('-entry_date')[:30])

            if recent_entries:
                last_date = recent_entries[0].entry_date.strftime('%d/%m/%Y')
                first_date = recent_entries[-1].entry_date.strftime('%d/%m/%Y')

                charcoal_recent_stats = {
                    'average_moisture': sum(entry.moisture for entry in recent_entries) / len(recent_entries),
                    'average_fines': sum(entry.fines for entry in recent_entries) / len(recent_entries),
                    'average_density': sum(entry.density for entry in recent_entries) / len(recent_entries),
                    'period': f'{first_date} - {last_date}',
                    'count': len(recent_entries),
                }
            else:
                charcoal_recent_stats = None

            supplier_data = {
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
                'charcoal_recent_stats': charcoal_recent_stats,
            }

            data.append(supplier_data)

        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_materials(request):
    try:
        materials = Supplier.objects.values_list('material_type', flat=True)
        materials_list = sorted(set(materials))

        return JsonResponse(materials_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
