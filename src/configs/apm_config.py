import os

from typing import Final

import elasticapm
from elasticapm.base import Client

# from dotenv import load_dotenv
# load_dotenv() # Take environment variables from .env

DEFAULT_APM_SERVICE_NAME: Final[str] = 'python_service'
DEFAULT_APM_SERVER_URL: Final[str] = 'http://192.168.0.100:8200'
DEFAULT_APM_ENVIRONMENT: Final[str] = 'Development'

apm: Client = elasticapm.Client(
    service_name = os.getenv('APM_SERVICE_NAME') or DEFAULT_APM_SERVICE_NAME,
    server_url = os.getenv('APM_SERVER_URL') or DEFAULT_APM_SERVER_URL,
    environment = os.getenv('APM_ENVIRONMENT') or DEFAULT_APM_ENVIRONMENT
)

# Automatically instrumenting app's http requests, database queries, etc.
elasticapm.instrument()