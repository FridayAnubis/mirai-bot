from contextlib import contextmanager
from contextvars import ContextVar
from inspect import currentframe
from typing import Any

debug = ContextVar('debug')
application = ContextVar('application')


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
    local_vars = currentframe().f_back.f_locals.items()

    context_var = None
    for name, value in local_vars:
        if name == var_name:
            context_var: ContextVar = value
    if context_var:
        return context_var.get()
    else:
        raise ValueError(f"context('{var_name}') not exits!")


if __name__ == '__main__':
    enter_context('test')
