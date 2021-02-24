from asyncio import AbstractEventLoop
from datetime import datetime
from typing import (
    Iterable,
    List,
    Optional,
)

from core.broadcast import Broadcast
from core.broadcast import Decorator
from core.broadcast import BaseDispatcher
from .task import SchedulerTask
from .exception import (
    RegisteredSchedule,
    InvalidSchedule,
)

Timer = Iterable[datetime]


class KarakoScheduler:
    loop: AbstractEventLoop
    broadcast: Broadcast
    schedule_tasks: List[SchedulerTask]

    def __init__(self, loop: AbstractEventLoop, broadcast: Broadcast) -> None:
        self.schedule_tasks = []
        self.loop = loop
        self.broadcast = broadcast

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
            self.schedule_tasks.remove(schedule)
        else:
            raise InvalidSchedule(
                    "schedule tasks not contain '{}'".format(schedule)
            )

    def schedule(self, timer: Timer, cancelable: Optional[bool] = False,
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
