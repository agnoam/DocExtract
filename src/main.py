import os
import sys

from elasticapm.traces import Span, Transaction

from .constants.defaults_constatns import DEFAULT_RECEIVE_DOCX_QUEUE_NAME
from .configs.apm_config import apm
from .configs.etcd_config import ETCDConfig, ETCDConnectionConfigurations, ETCDModuleConfigs, EtcdConfigurations
from .configs.rabbit_config import RabbitDriver, RabbitQueue

def main() -> None:
    try:
        transaction: Transaction = apm.begin_transaction('background_process')
        transaction.name = 'Boot Initialization'
        
        service_initialization(transaction)

        apm.end_transaction(name = transaction.name)
        RabbitDriver.listen() # Must be the last line of the script

    except KeyboardInterrupt:
        print('Interrupted')
        try:
            RabbitDriver.close_connection()
            sys.exit(0)
        except SystemExit:
            os._exit(0)

def service_initialization(transaction: Transaction) -> None:
    """
        Initializing the connections the service uses
    """
    ETCDConfig(
        connection_configurations=ETCDConnectionConfigurations(
            host=os.getenv("ETCD_HOST")
        ),
        user_defined_configs=EtcdConfigurations(
            module_configs=ETCDModuleConfigs(
                
            ),
            environment_params={
                'RABBIT_QUEUE_RECIEVE_DOCX': DEFAULT_RECEIVE_DOCX_QUEUE_NAME
            }
        )
    )

    RabbitDriver.initialize_rabbitmq({
        # RABBIT_QUEUE_IMAGES_TO_RECOGNIZE: RabbitQueue(callback=image_to_recognize_handler),
        # RABBIT_QUEUE_FOUND_FACES: RabbitQueue()
    })

if __name__ == "__main__":
    main()