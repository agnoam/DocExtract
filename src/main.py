import os
import sys
from typing import Final

from elasticapm.traces import Span, Transaction

from constants.apm_constants import TransactionTypes, SpanTypes
from constants.app_constatns import DEFAULT_RECEIVE_DOCX_QUEUE_NAME
from configs.apm_config import apm
from configs.etcd_config import ETCDConfig, ETCDConnectionConfigurations, ETCDModuleConfigs, EtcdConfigurations
from configs.rabbit_config import RabbitDriver, RabbitQueue
from handlers.rabbit_handlers import receive_docx_handler

def main() -> None:
    try:
        transaction: Transaction = apm.begin_transaction(TransactionTypes.BACKGROUND_PROCESS)
        transaction.name = 'Boot Initialization'
        
        service_initialization(transaction)

        apm.end_transaction(name = transaction.name)
        RabbitDriver.listen() # Must be the last line of the script

    except KeyboardInterrupt:
        print('Script interrupted')
        try:
            RabbitDriver.close_connection()
            sys.exit(0)
        except SystemExit:
            os._exit(0)

def service_initialization(transaction: Transaction=None) -> None:
    """
        Initializing the connections the service uses
    """
    etcd_span: Span = transaction.begin_span('ETCD setup', SpanTypes.TASK)
    ETCDConfig(
        connection_configurations=ETCDConnectionConfigurations(
            host=os.getenv("ETCD_HOST")
        ),
        user_defined_configs=EtcdConfigurations(
            module_configs=ETCDModuleConfigs(
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
    RabbitDriver.initialize_rabbitmq({
        RECIEVED_DOCX_QUEUE: RabbitQueue(callback=receive_docx_handler)
    })
    rabbit_span.end()

if __name__ == "__main__":
    main()