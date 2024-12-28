import re

from django.http import HttpRequest, JsonResponse

from gelfmp.models import CharcoalEntry, Document, DocumentType, Supplier


def get_charcoal_recent_stats(recent_entries):
    if recent_entries:
        last_date = recent_entries[0].entry_date.strftime('%d/%m/%Y')
        first_date = recent_entries[-1].entry_date.strftime('%d/%m/%Y')

        return {
            'average_moisture': sum(entry.moisture for entry in recent_entries) / len(recent_entries),
            'average_fines': sum(entry.fines for entry in recent_entries) / len(recent_entries),
            'average_density': sum(entry.density for entry in recent_entries) / len(recent_entries),
            'period': f'{first_date} - {last_date}',
            'count': len(recent_entries),
        }

    return None


def get_suppliers(request: HttpRequest):
    try:
        suppliers = Supplier.objects.select_related('city', 'state').all()
        data = []

        for supplier in suppliers:
            recent_entries = list(CharcoalEntry.objects.filter(supplier=supplier).order_by('-entry_date')[:30])
            charcoal_recent_stats = get_charcoal_recent_stats(recent_entries)

            # Calcula a média dos ultimos 3 IQFs existentes,
            # caso não existam, define rating como None.
            iqfs = supplier.get_iqfs().all()[:3].values_list('iqf', flat=True)
            rating = f'{round(sum(iqfs) / len(iqfs), 1):.1f}' if len(iqfs) == 3 else None

            supplier_visible_documents = [
                {
                    'id': document.id,
                    'name': document.name,
                    'type': document.get_document_type_display(),
                    'filepath': document.file.url,
                    'validity': document.validity,
                }
                for document in supplier.get_visible_documents()
            ]

            supplier_data = {
                'id': supplier.id,
                'corporate_name': supplier.corporate_name,
                'cpf_cnpj': supplier.cpf_cnpj,
                'material_type': supplier.material_type,
                'rating': rating,
                'state': {
                    'abbr': supplier.state.abbr,
                    'name': supplier.state.name,
                },
                'city': {
                    'id': supplier.city.id,
                    'name': supplier.city.name,
                },
                'distance_in_meters': supplier.distance_in_meters,
                'documents': supplier_visible_documents,
                'charcoal_recent_stats': charcoal_recent_stats,
            }

            data.append(supplier_data)

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_state_shapefiles(request: HttpRequest, state):
    if not re.match(r'^[A-Z]{2}$', state):
        return JsonResponse({'error': 'Invalid state code.'}, status=400)

    property_shapefiles = Document.objects.filter(
        document_type=DocumentType.PROPERTY_SHAPEFILE,
        supplier__state=state.upper(),
    ).values('id', 'name', 'supplier__corporate_name', 'geojson')

    shapefiles = Document.objects.filter(
        document_type=DocumentType.SHAPEFILE,
        supplier__state=state.upper(),
    ).values('id', 'name', 'supplier__corporate_name', 'geojson')

    data = [
        {
            'supplier_name': doc.pop('supplier__corporate_name'),
            'id': doc.pop('id'),
            'name': doc.pop('name'),
            'geojson': doc.pop('geojson'),
        }
        for doc in property_shapefiles
    ] + [
        {
            'supplier_name': doc.pop('supplier__corporate_name'),
            'id': doc.pop('id'),
            'name': doc.pop('name'),
            'geojson': doc.pop('geojson'),
        }
        for doc in shapefiles
    ]

    return JsonResponse(
        data,
        safe=False,
    )
