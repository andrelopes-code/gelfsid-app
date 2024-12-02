import functools

from django.template.loader import render_to_string

from gelfsid.logger import logger


def handle_chart_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except (ValueError, KeyError) as e:
            logger.error(f'at: {func.__module__}.{func.__name__} | {e}')
            return render_to_string('components/errors/chart_error.html', {'error': str(e)})

        except Exception as e:
            logger.error(f'at: {func.__module__}.{func.__name__} | {e}')
            return render_to_string('components/errors/internal.html')

    return wrapper
