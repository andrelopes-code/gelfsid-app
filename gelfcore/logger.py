import sys
from pathlib import Path

from django.conf import settings
from loguru import logger

BASE_DIR = Path(__file__).resolve().parent.parent

logger.remove()

if settings.DEBUG:
    logger.add(
        sys.stderr,
        level='INFO',
        format='{time} | {name} | {level} | {message}',
        colorize=True,
    )

logger.add(
    f'{BASE_DIR}/logs/error.log',
    rotation='00:00',
    retention='7 days',
    level='ERROR',
    format='{time} | {name} | {level} | {message}',
)
