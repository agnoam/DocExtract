from typing import Any

from elasticapm.traces import Span, Transaction
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from ..configs.apm_config import apm
from ..constants.apm_constants import TransactionTypes

def receive_docx_handler(
    channel: Channel, method: Basic.Deliver, 
    properties: BasicProperties, body: Any
) -> None:
    try:
        transaction: Transaction = apm.begin_transaction(TransactionTypes.QUEUE_HANDLER)
        transaction.name = 'Receive docx handler'
        # transaction
    except Exception as ex:
        apm.capture_exception(ex)
        print(f'rabbitmq_callback exception: {ex}', 'red')
    pass