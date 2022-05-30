from dataclasses import dataclass
import os
from typing import Any, List
from functools import wraps
from typing import Callable

import elasticapm
from elasticapm.base import Client
from elasticapm.traces import Span, Transaction, TraceParent

from constants.apm_constants import DefaultValues, SpanTypes, TransactionTypes

# from dotenv import load_dotenv
# load_dotenv() # Take environment variables from .env

# TODO: Create decorator for tracking a transaction and span
apm: Client = elasticapm.Client(
    service_name = os.getenv('APM_SERVICE_NAME', DefaultValues.APM_SERVICE_NAME),
    server_url = os.getenv('APM_SERVER_URL', DefaultValues.APM_SERVER_URL),
    environment = os.getenv('APM_ENVIRONMENT', DefaultValues.APM_ENVIRONMENT)
)

def create_transaction(
    name: str, 
    transaction_type: TransactionTypes = TransactionTypes.DEFAULT, 
    trace_parent: TraceParent = None
) -> Transaction:
    transaction: Transaction = apm.begin_transaction(transaction_type.value, trace_parent)
    transaction.name = name

    return transaction

def end_transaction(transaction: Transaction) -> None:
    if isinstance(transaction, Transaction):
        apm.end_transaction(transaction.name)
    else:
        print('Cannot end arg that not a transaction')


# When you want the decorator to create the transaction use this class
@dataclass
class TransactionCreationData:
    name: str
    type: TransactionTypes

def __create_transaction(_transaction: Transaction | TransactionCreationData, func: Callable, kwargs: dict) -> tuple[Transaction, dict[str, Any], bool]:
    """
        This function will create the transaction in case it needed (from type TransactionCreationData)
        Or will get it from the kwargs.
        And will delete the transaction from the kwargs if needed.

        args:
            _transaction: Transaction | TransactionCreationData - The transaction object or instructions to create it
            func: Callable - The function the will be run after the decorator
            kwargs: dict - The kwargs passed into the target function

        returns:
            [created_transaction, kwargs, is_transaction_created] - from types [Transaction, dict[str, Any], bool] respectively
    """

    try:
        is_transaction_created: bool = False

        # Create transaction from data
        if isinstance(_transaction, TransactionCreationData):
            _transaction = create_transaction(_transaction.name, _transaction.type)
            is_transaction_created = True

        if not _transaction:
            # Dynamically changed transaction support (in kwargs)
            _transaction: Transaction = kwargs['transaction']
            
            # Removing the transaction kwarg, just in case the function does not use it at all
            if not 'transaction' in func.__code__.co_varnames:
                kwargs.pop('transaction', None)
        
        if not _transaction:
            raise Exception(f'Can not trace {func.__name__} function without a transaction')
        
        return _transaction, kwargs, is_transaction_created
    except Exception as ex:
        raise Exception(ex)

# The name of the function is the name of the decorator ("decorator factory")
def trace_function(
    transaction: Transaction | TransactionCreationData = None,
    span_type: SpanTypes | None = None, 
    span_name: str | None = None,
    close_transaction: bool = False
) -> None:
    def trace_decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _transaction, kwargs, is_transaction_created = __create_transaction(transaction, func, kwargs)
            if not is_transaction_created: span: Span = _transaction.begin_span(span_name or func.__name__, span_type)
            
            # In case we want the transaction to close automatically, 
            # the decorator will inject the transaction into the function for further use
            if close_transaction: kwargs['transaction'] = _transaction
            res = func(*args, **kwargs)

            if not is_transaction_created: span.end()
            if close_transaction: end_transaction(_transaction)

            return res
        return wrapper
    return trace_decorator

# Automatically instrumenting app's http requests, database queries, etc.
elasticapm.instrument()