from typing import (
    Callable,
    Dict,
    List,
    Union,
)

from .decorator import Decorator
from ..typing import T_Dispatcher


class ExecTarget:
    def __init__(
            self,
            callable_: Callable,
            inline_dispatchers: List[T_Dispatcher] = None,
            headless_decorators: List[Decorator] = None,
            enable_internal_access: bool = False,
    ) -> None:
        self.callable = callable_
        self.inline_dispatchers = inline_dispatchers or []
        self.headless_decorators = headless_decorators or []
        self.enable_internal_access = enable_internal_access

        self.dispatcher_statistics = {
            "total": 0,
            "statistics": {}
        }

    callable: Callable
    inline_dispatchers: List[T_Dispatcher] = []
    headless_decorators: List[Decorator] = []
    enable_internal_access: bool = False

    dispatcher_statistics: Dict[str, Union[int, Dict]]
