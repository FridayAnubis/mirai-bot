from abc import (
    abstractmethod,
    ABCMeta,
)
from typing import Type

from .dispatcher import BaseDispatcher
from .event import BaseEvent
from ..abstract.interfaces.dispatcher import IDispatcherInterface


class BaseRule(metaclass=ABCMeta):
    target_dispatcher: BaseDispatcher

    def __init__(self, target_dispatcher: BaseDispatcher) -> None:
        self.target_dispatcher = target_dispatcher

    @abstractmethod
    def check(self, event: BaseEvent, dii: IDispatcherInterface) -> bool:
        pass


class SpecialEventType(BaseRule):
    target_dispatcher: BaseDispatcher

    def __init__(
            self,
            event_type: Type[BaseEvent],
            target_dispatcher: BaseDispatcher,
            specially: bool = False
    ) -> None:
        super().__init__(target_dispatcher)
        self.target_dispatcher = target_dispatcher
        self.event_type = event_type
        self.specially = specially

    def check(self, event: BaseEvent, dii: IDispatcherInterface) -> bool:
        if self.specially:
            if type(event) is self.event_type:
                return True
        else:
            if isinstance(event, self.event_type):
                return True
