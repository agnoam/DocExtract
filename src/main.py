import os
import sys
from typing import Final

from pika.credentials import PlainCredentials
from elasticapm.traces import Span, Transaction

from constants.apm_constants import TransactionTypes, SpanTypes
from constants.app_constatns import DEFAULT_RECEIVE_DOCX_QUEUE_NAME
from constants.rabbit_constants import EnvKeys as RabbitEnvKeys
from configs.apm_config import apm
from configs.etcd_config import ETCDConfig, ETCDConnectionConfigurations, ETCDModuleOptions, EtcdConfigurations
from configs.rabbit_config import RabbitDriver, RabbitQueue
from handlers.rabbit_handlers import receive_docx_handler

def main() -> None:
    try:
        transaction: Transaction = apm.begin_transaction(TransactionTypes.BACKGROUND_PROCESS)
        transaction.name = 'Boot Initialization'
        
        service_initialization()

        apm.end_transaction(name = transaction.name)
        RabbitDriver.listen() # Must be the last line of the script

    except KeyboardInterrupt:
        print('Script interrupted')
        try:
            RabbitDriver.close_connection()
            sys.exit(0)
        except SystemExit:
            os._exit(0)

def service_initialization(transaction: Transaction) -> None:
    """
        Initializing the connections the service uses
    """
    etcd_span: Span = transaction.begin_span('ETCD setup', SpanTypes.TASK)
    ETCDConfig(
        connection_configurations=ETCDConnectionConfigurations(
            host=os.getenv("ETCD_HOST")
        ),
        user_defined_configs=EtcdConfigurations(
            module_configs=ETCDModuleOptions(
                override_sys_object=True,
                gen_keys=True
            ),
            environment_params={
                'RABBIT_QUEUE_RECIEVE_DOCX': DEFAULT_RECEIVE_DOCX_QUEUE_NAME
            }
        )
    )
    etcd_span.end()

    rabbit_span: Span = transaction.begin_span('RabbitMQ setup', SpanTypes.TASK)
    RECIEVED_DOCX_QUEUE: Final[str] = os.getenv('RABBIT_QUEUE_RECIEVE_DOCX', DEFAULT_RECEIVE_DOCX_QUEUE_NAME)
    
    # Optional, in case use have changed the default credentials
    username: Final[str] = os.getenv(RabbitEnvKeys.RABBIT_USERNAME)
    password: Final[str] = os.getenv(RabbitEnvKeys.RABBIT_PASSWORD)

    RabbitDriver.initialize_rabbitmq(
        credentials=PlainCredentials(username, password), # Optional
        queues_configurations={
            RECIEVED_DOCX_QUEUE: RabbitQueue(callback=receive_docx_handler)
        }
    )
    rabbit_span.end()

if __name__ == "__main__":
    main()