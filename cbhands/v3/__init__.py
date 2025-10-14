"""cbhands v3.0.0 - Extensible service manager."""

__version__ = "3.0.0"
__author__ = "Battle Hands Team"
__description__ = "Extensible service manager for Battle Hands with plugin system"

from .main import main, create_app
from ..core import *

__all__ = [
    'main',
    'create_app',
    '__version__',
    '__author__',
    '__description__',
]
