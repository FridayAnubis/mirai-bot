from contextlib import contextmanager
from contextvars import ContextVar
from inspect import currentframe
from typing import Any

bot = ContextVar('bot')
application = ContextVar('application')
logger = ContextVar('logger')
debug = ContextVar('debug')


@contextmanager
def enter_context(context: str, value: Any = None):
    token = None

    context_value = None
    for n, v in currentframe().f_back.f_locals.items():
        if n == context:
            context_value: ContextVar = v
    if not context_value:
        raise ValueError(f"context('{context}') not exits!")

    if value:
        token = context_value.set(value)
    yield
    try:
        if token:
            context_value.reset(token)
    except ValueError:
        ...


def get_var(var_name: str):
    try:
        return eval(f'{var_name}.get()')
    except (NameError, AttributeError, LookupError):
        raise ValueError(f"Context('{var_name}') not exits!")


def set_var(var_name: str, value: Any):
    try:
        return eval(var_name).set(value)
    except (NameError, AttributeError):
        raise ValueError(f"Context('{var_name}') not exits!")
