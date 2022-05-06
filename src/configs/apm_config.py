import os

import elasticapm
from elasticapm.base import Client

from ..constants.apm_constants import DefaultValues

# from dotenv import load_dotenv
# load_dotenv() # Take environment variables from .env

apm: Client = elasticapm.Client(
    service_name = os.getenv('APM_SERVICE_NAME') or DefaultValues.APM_SERVICE_NAME,
    server_url = os.getenv('APM_SERVER_URL') or DefaultValues.APM_SERVER_URL,
    environment = os.getenv('APM_ENVIRONMENT') or DefaultValues.APM_ENVIRONMENT
)

# Automatically instrumenting app's http requests, database queries, etc.
elasticapm.instrument()