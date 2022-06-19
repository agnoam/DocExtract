from typing import Any

from elasticapm.traces import Span, Transaction
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from configs.apm_config import TransactionCreationData, apm, trace_function
from constants.apm_constants import TransactionTypes

@trace_function(
    transaction=TransactionCreationData('Receive docx file', TransactionTypes.QUEUE_HANDLER),
    close_transaction=True
)
def receive_docx_handler(
    channel: Channel, method: Basic.Deliver,
    properties: BasicProperties, body: Any,
    **kwargs
) -> None:
    # Load transaction to pass it trough (just in case @trace_function has close_transaction property)
    transaction: Transaction = kwargs['transaction']
    try:
        # span: Span = transaction.begin_span('handler_test', SpanTypes.TASK)
        print('Received a message', {
            'channel': channel, 
            'method': method, 
            'properties': properties,
            'body': body,
            'transaction': transaction
        })
        # span.end()
        # end_transaction(transaction)

        channel.basic_ack(method.delivery_tag)
    except Exception as ex:
        apm.capture_exception(ex)
        print(f'Caught rabbitmq_callback exception: {ex}', 'red')