from django.http import JsonResponse

from map import charts

CHARTS = {
    'charcoal_entries': charts.charcoal_entries,
    'moisture_and_fines_by_day': charts.moisture_and_fines_by_day,
    'density_by_day': charts.density_by_day,
}


def update_chart(request):
    try:
        chart_id = request.GET.get('chart_id')
        if not chart_id or chart_id not in CHARTS:
            return JsonResponse({'error': 'Missing or invalid chart_id'}, status=400)

        filters = {key: value for key, value in request.GET.items() if key != 'chart_id'}
        updated_chart_json = CHARTS[chart_id](**filters)

        return JsonResponse({'updated_chart': updated_chart_json}, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
