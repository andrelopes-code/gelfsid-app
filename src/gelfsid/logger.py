import sys
from pathlib import Path

from loguru import logger

BASE_DIR = Path(__file__).resolve().parent.parent.parent

logger.remove()

logger.add(
    sys.stderr,
    level='INFO',
    format='{time} | {level} | {message}',
    colorize=True,
)

logger.add(
    f'{BASE_DIR}/logs/app.log',
    rotation='00:00',
    retention='7 days',
    level='DEBUG',
    format='{time} | {level} | {message}',
)
