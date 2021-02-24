from contextlib import contextmanager
from contextvars import ContextVar
from inspect import currentframe
from typing import Any

application = ContextVar('application')
bot = ContextVar('bot')


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
        raise ValueError(f"context('{var_name}') not exits!")
