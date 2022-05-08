from typing import Final

class DefaultValues:
    APM_SERVICE_NAME: Final[str] = 'python_service'
    APM_SERVER_URL: Final[str] = 'http://localhost:8200'
    APM_ENVIRONMENT: Final[str] = 'Development'

class TransactionTypes:
    BACKGROUND_PROCESS: Final[str] = 'background_process'
    QUEUE_HANDLER: Final[str] = 'queue_handler'

class SpanTypes:
    TASK: Final[str] = 'task'