from logging import debug
import threading
from typing import Any, Callable
import pika
from pika import SelectConnection
import os
from pika.connection import ConnectionParameters
from pika.spec import Basic, BasicProperties
from pika.channel import Channel

# from .src.constants.constants import RABBIT_HOST_ENV_KEY, RABBIT_PORT_ENV_KEY

# from dotenv import load_dotenv
# load_dotenv() # Take environment variables from .env.

class RabbitQueue:
    '''
        Callback can be none, because it can be used just for publishing data
    '''
    def __init__(
        self, 
        callback: Callable[[Channel, Basic.Deliver, BasicProperties, Any], None] = None,
        auto_ack: bool = False, exclusive: bool = False,
        consumer_tag: str = None, arguments: dict[str, dict] = {}, 
        exchange_name: str = '', is_new_channel: bool = False
    ) -> None:        
        self.callback = callback
        self.auto_ack = auto_ack
        self.exclusive = exclusive
        self.consumer_tag = consumer_tag
        self.arguments = arguments
        self.exchange_name = exchange_name
        self.is_new_channel = is_new_channel

class RabbitDriver:
    connection: SelectConnection = None
    default_channel: Channel = None

    ''' Format of this dictionary like this: { queue_name: RabbitQueue (class) } '''
    queues_configurations: dict[str, RabbitQueue] = {}
    ''' Format of this dictionary like this: { queue_name: parent_channel } '''
    active_channels: dict[str, Channel] = {}

    @classmethod
    def initialize_rabbitmq(
        cls,
        queues_configurations: dict[str, RabbitQueue],
        host: str = None,
        port: int = None,
        credentials: Any = None
    ) -> None:
        cls.queues_configurations = queues_configurations
        cls.__initialize_connection(host)

    @classmethod
    def __initialize_connection(
        cls, host: str = None, 
        port: int = None, credentials = None
    ) -> None:
        print('__initialize_connection() executing')

        if host is None:
            host = str(os.getenv(RABBIT_HOST_ENV_KEY))

        parameters: ConnectionParameters = pika.ConnectionParameters(host)

        # Priority of port: manually set (arg), ENV, _DEFAULT
        if str(os.getenv(RABBIT_PORT_ENV_KEY)) is not None and port is None:
            port = int(os.getenv(RABBIT_PORT_ENV_KEY))
            parameters.port = port

        cls.connection = pika.SelectConnection(
            parameters = parameters, 
            on_open_callback = lambda connection: cls.__setup_channels(connection),
            on_close_callback = lambda event: print(f'connection closed (by {event} event)')
        )
        
    @classmethod
    def __setup_channels(
        cls, connection: SelectConnection
    ) -> None:
        print('__setup_channels() executing')
        assert connection is not None, 'Cannot set up channels without active connection'
        
        # A channel for sending messages
        cls.default_channel = cls.connection.channel()

        # Queues callback channel (channel that receives all the queues callbacks)
        cls.connection.channel(on_open_callback = cls.__assign_channel)

    @classmethod
    def __assign_channel(cls, channel: Channel) -> None:
        print('__assign_channel() executing')

        # Open new thread on each queue and saving
        for queue_name in cls.queues_configurations:
            cls.__setup_queue(queue_name, cls.queues_configurations[queue_name], channel)
        
        cls.active_channels[queue_name] = channel

    @classmethod
    def __setup_queue(cls, queue_name: str, queue_declaration: RabbitQueue, channel: Channel) -> None:
        print('__setup_queue() executing')

        channel.queue_declare(queue=queue_name)
        
        ''' In case the queue_configuration has a callback function, it means the user want to set a consumer '''
        if queue_declaration.callback is not None:            
            channel.basic_consume(
                queue_name,
                lambda *_args: threading.Thread(
                    name=f'rabbitmq_queue_handler:{queue_name}', 
                    target=queue_declaration.callback, args=_args
                ).start(),
                auto_ack = queue_declaration.auto_ack,
                exclusive = queue_declaration.exclusive,
                consumer_tag = queue_declaration.consumer_tag,
                arguments = queue_declaration.arguments
            )
        
    @classmethod
    def get_channel(cls) -> Channel:
        print('get_channel() executing')
        _channel: Channel = cls.default_channel

        if _channel is not None:
            return _channel
        
        raise Exception('There queue is not handled in any channel')

    @classmethod
    def listen(cls) -> None:
        print('listen() executing')

        err_message: str = "There is no declared connection, don't forget to call initialize_rabbitmq() method before"
        assert cls.connection is not None, err_message

        print('Starting to listen by io loop')
        cls.connection.ioloop.start()

    @classmethod
    def close_connection(cls) -> None:
        print('close_connection() executing')

        for queue_name in cls.active_channels:
            try:
                cls.active_channels[queue_name].close()
            except Exception as ex:
                debug(f'Can not close {queue_name}. ex: ', ex)

        cls.connection.close()