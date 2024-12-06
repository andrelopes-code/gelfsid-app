from functools import wraps

from django.template.loader import render_to_string

from gelfcore.logger import log


def handle_chart_error(function):
    """Decorador para lidar com erros em funções que geram gráficos plotly."""

    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)

        except (ValueError, KeyError) as e:
            log.error(f'at: {function.__module__}.{function.__name__} | {e}')
            return render_to_string('components/errors/chart_error.html', {'error': str(e)})

        except Exception as e:
            log.error(f'at: {function.__module__}.{function.__name__} | {e}')
            return render_to_string('components/errors/internal.html')

    return wrapper
