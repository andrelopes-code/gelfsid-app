import sys

from django.conf import settings
from loguru import logger

from gelfmp.models.app_error import AppError

logger.remove()
log = logger

# Caso a aplicação seja iniciada com o
# debug habilitado, loga em stderr (terminal)
if settings.DEBUG:
    log.add(
        sys.stderr,
        level='INFO',
        format='{time} | {name} | {level} | {message}',
        colorize=True,
    )
else:
    # Configura o logger para logar em um arquivo
    # de erro com rotação de 7 dias e level de erro
    log.add(
        f'{settings.BASE_DIR}/logs/error.log',
        rotation='00:00',
        retention='7 days',
        level='ERROR',
        format='{time} | {name} | {level} | {message}',
    )


def log_service_error(error_origin, error_message):
    AppError.objects.create(
        error_message=error_message,
        error_origin=error_origin,
    )
