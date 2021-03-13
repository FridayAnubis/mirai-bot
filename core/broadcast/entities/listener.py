from typing import (
    Callable,
    List,
    Type,
    Union,
)

from .dispatcher import BaseDispatcher
from .event import BaseEvent
from .namespace import Namespace
from .decorator import Decorator

from .exectarget import ExecTarget


class Listener(ExecTarget):
    def __init__(
            self,
            callable_: Callable,
            namespace: Namespace,
            listening_events: Union[List[Type[BaseEvent]], Type[BaseEvent]],
            inline_dispatchers: List[BaseDispatcher] = None,
            headless_decorators: List[Decorator] = None,
            priority: int = 16,
            enable_internal_access: bool = False,
    ) -> None:
        super().__init__(
            callable_, inline_dispatchers, headless_decorators,
            enable_internal_access
        )
        self.namespace = namespace
        self.listening_events = [listening_events] if not isinstance(
            listening_events, list) else listening_events
        self.priority = priority

    namespace: Namespace
    listening_events: List[Type[BaseEvent]]
    priority: int = 16
