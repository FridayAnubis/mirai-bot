from ..entities.dispatcher import BaseDispatcher
from ..entities.event import BaseEvent
from ..abstract.interfaces.dispatcher import IDispatcherInterface


class ExceptionThrew(BaseEvent):
    exception: Exception
    event: BaseEvent

    def __init__(self, exception: Exception, event: BaseEvent):
        self.exception = exception
        self.event = event

    class Dispatcher(BaseDispatcher):
        @staticmethod
        def catch(interface: IDispatcherInterface):
            if interface.annotation == interface.event.exception.__class__:
                return interface.event.exception
            if interface.name == "event":
                return interface.event.event
