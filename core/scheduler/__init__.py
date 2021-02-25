from asyncio import AbstractEventLoop
from typing import (
    List,
    Optional,
    Union,
)

from core.broadcast import (
    BaseDispatcher,
    Namespace,
)
from core.broadcast import Broadcast
from core.broadcast import Decorator
from utils.typing import Timer
from .exception import (
    RegisteredSchedule,
    InvalidSchedule,
    AlreadyStarted,
)
from .task import SchedulerTask


class KarakoScheduler:
    loop: AbstractEventLoop
    broadcast: Broadcast
    schedule_tasks: List[SchedulerTask]
    namespaces: List[Namespace]

    def __init__(self, loop: AbstractEventLoop, broadcast: Broadcast) -> None:
        self.schedule_tasks = []
        self.loop = loop
        self.broadcast = broadcast
        self.namespaces = []

    def containNamespace(self, name) -> bool:
        for namespace in self.namespaces:
            if namespace.name == name:
                return True
        return False

    def getNamespace(self, name) -> Namespace:
        if self.containNamespace(name):
            for namespace in self.namespaces:
                if namespace.name == name:
                    return namespace
        else:
            return None

    def createNamespace(self, name, *, priority: int = 0, hide: bool = False,
                        disabled: bool = False) -> Namespace:
        result = self.getNamespace(name)
        if result is not None:
            return result
        result = Namespace(name=name, priority=priority, hide=hide,
                           disabled=disabled)
        self.namespaces.append(result)
        return result

    def removeNamespace(self, name: str):
        result = self.getNamespace(name)
        if result is not None:
            self.namespaces.remove(result)
            for schedule_task in self.schedule_tasks:
                if schedule_task.namespace.name == name:
                    self.removeNamespace(schedule_task)

    def enableNamespace(self, name: Union[str, Namespace]):
        namespace = name if isinstance(name, Namespace) else \
            self.getNamespace(name)
        if namespace is not None:
            for schedule_task in self.schedule_tasks:
                if schedule_task.namespace == namespace:
                    try:
                        schedule_task.setup_task()
                    except AlreadyStarted:
                        continue

    def disableNamespace(self, name: Union[str, Namespace]):
        namespace = name if isinstance(name, Namespace) else \
            self.getNamespace(name)
        if namespace is not None:
            for schedule_task in self.schedule_tasks:
                if schedule_task.namespace == namespace:
                    schedule_task.stop()

    def containSchedule(self, schedule: SchedulerTask) -> bool:
        return schedule in self.schedule_tasks

    def addSchedule(self, schedule: SchedulerTask):
        if self.containSchedule(schedule):
            raise RegisteredSchedule(
                '"{}" has been registered!'.format(schedule)
            )
        else:
            self.schedule_tasks.append(schedule)

    def removeSchedule(self, schedule: SchedulerTask):
        if self.containSchedule(schedule):
            schedule.stop()
            self.schedule_tasks.remove(schedule)
        else:
            raise InvalidSchedule(
                "Schedule tasks not contain '{}'".format(schedule)
            )

    def schedule(
            self,
            timer: Timer,
            *,
            cancelable: Optional[bool] = False,
            decorators: Optional[List[Decorator]] = None,
            dispatchers: List[BaseDispatcher] = None,
            enableInternalAccess: Optional[bool] = False
    ):
        def wrapper(func):
            schedulerTask = SchedulerTask(
                func, timer, self.broadcast, self.loop, cancelable,
                dispatchers, decorators, enableInternalAccess
            )
            self.addSchedule(schedulerTask)
            schedulerTask.setup_task()
            return func

        return wrapper
