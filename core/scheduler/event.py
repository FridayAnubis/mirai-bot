from core.broadcast import BaseDispatcher
from core.broadcast import BaseEvent
from core.broadcast.interfaces.dispatcher import DispatcherInterface


class SchedulerTaskExecute(BaseEvent):
    class Dispatcher(BaseDispatcher):
        def catch(self: DispatcherInterface):
            ...
