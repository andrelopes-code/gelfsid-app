import sys
from pathlib import Path

from django.conf import settings
from loguru import logger

BASE_DIR = Path(__file__).resolve().parent.parent
logger.remove()
log = logger

if settings.DEBUG:
    # Log no terminal
    logger.add(
        sys.stderr,
        level='INFO',
        format='{time} | {name} | {level} | {message}',
        colorize=True,
    )

# Log em arquivo /logs/error.log
logger.add(
    f'{BASE_DIR}/logs/error.log',
    rotation='00:00',
    retention='7 days',
    level='ERROR',
    format='{time} | {name} | {level} | {message}',
)
