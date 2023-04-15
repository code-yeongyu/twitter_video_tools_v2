import logging

from rich.console import Console
from rich.logging import RichHandler

console = Console()
logger = logging.getLogger('rich')

logging.basicConfig(level=logging.NOTSET, format='%(message)s', datefmt='[%X]', handlers=[RichHandler()])
