from enum import Enum
from typing import Final

class DefaultValues(Enum):
    APM_SERVICE_NAME: Final[str] = 'python_service'
    APM_SERVER_URL: Final[str] = 'http://localhost:8200'
    APM_ENVIRONMENT: Final[str] = 'Development'

class TransactionTypes(Enum):
    BACKGROUND_PROCESS: Final[str] = 'background_process'
    QUEUE_HANDLER: Final[str] = 'queue_handler'
