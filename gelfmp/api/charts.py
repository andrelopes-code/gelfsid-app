from inspect import getmembers, isfunction, signature

from django.http import HttpRequest, JsonResponse

from gelfcore.logger import log
from gelfmp.charts import charts

CHARTS = {name: obj for name, obj in getmembers(charts, isfunction)}
CHARTS_ARGS = {chart_id: set(signature(func).parameters.keys()) for chart_id, func in CHARTS.items()}


def update_chart(request: HttpRequest):
    try:
        chart_id = request.GET.get('chart_id')
        if not chart_id or chart_id not in CHARTS:
            return JsonResponse({'error': 'Missing or invalid chart_id'}, status=400)

        chart_function = CHARTS[chart_id]
        accepted_args = CHARTS_ARGS[chart_id]

        args = {key: value for key, value in request.GET.items() if key in accepted_args}
        updated_chart_json = chart_function(**args)

        return JsonResponse({'chart_data': updated_chart_json}, safe=False)

    except Exception as e:
        log.error(str(e))
        return JsonResponse({'error': str(e)}, status=500)
