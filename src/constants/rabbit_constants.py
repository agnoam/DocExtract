from enum import Enum
from typing import Final

class EnvKeys(Enum):
    RABBIT_HOST: Final[str] = 'RABBIT_HOST'
    RABBIT_PORT: Final[str] = 'RABBIT_PORT'