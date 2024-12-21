from inspect import getmembers, isfunction, signature

from django.http import HttpRequest, JsonResponse

from gelfcore.logger import log
from gelfmp.charts import charts

CHARTS = {name: chart_func for name, chart_func in getmembers(charts, isfunction)}
CHART_ARGS = {name: set(signature(chart_func).parameters.keys()) for name, chart_func in CHARTS.items()}


def update_chart(request: HttpRequest):
    try:
        chart_id = request.GET.get('chart_id')

        if not chart_id or chart_id not in CHARTS:
            return JsonResponse({'error': 'Missing or invalid chart_id'}, status=400)

        chart_function = CHARTS[chart_id]
        chart_function_accepted_args = CHART_ARGS[chart_id]

        args = {arg: value for arg, value in request.GET.items() if arg in chart_function_accepted_args}
        updated_chart_json = chart_function(**args)

        return JsonResponse({'chart_data': updated_chart_json}, safe=False)

    except Exception as e:
        log.error(str(e))
        return JsonResponse({'error': str(e)}, status=500)
