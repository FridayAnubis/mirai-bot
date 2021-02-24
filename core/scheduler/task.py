from asyncio import (
    Task,
    AbstractEventLoop,
    sleep as Sleep,
    CancelledError,
    shield as Shield,
)
from datetime import datetime
from traceback import print_exc
from typing import (
    Any,
    Callable,
    Coroutine,
    Generator,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

from core.broadcast import BaseDispatcher
from core.broadcast import Broadcast
from core.broadcast import Decorator
from core.broadcast import ExecTarget
from core.scheduler.exception import AlreadyStarted
from core.scheduler.utilles import (
    EnteredRecord,
    print_track_async,
)
from utils.context import get_var
from utils.logger import Logger
from utils.typing import Timer
from .event import SchedulerTaskExecute


class SchedulerTask:
    target: Callable[..., Any]
    timer: "Timer"
    task: Task

    broadcast: Broadcast
    dispatchers: List[
        Union[
            Type[BaseDispatcher],
            Callable,
            BaseDispatcher]]
    decorators: List[Decorator]
    enableInternalAccess: bool = False

    cancelable: bool = False
    stopped: bool = False

    sleep_record: EnteredRecord
    started_record: EnteredRecord

    loop: AbstractEventLoop

    @property
    def is_sleeping(self) -> bool:
        return self.sleep_record.entered

    @property
    def is_executing(self) -> bool:
        return not self.sleep_record.entered

    def __init__(self,
                 target: Callable[..., Any],
                 timer: "Timer",
                 broadcast: Broadcast,
                 loop: AbstractEventLoop,
                 cancelable: bool = False,
                 dispatchers: Optional[
                     List[
                         Union[
                             Type[BaseDispatcher],
                             Callable,
                             BaseDispatcher]]] = None,
                 decorators: Optional[List[Decorator]] = None,
                 enableInternalAccess: bool = False) -> None:
        self.target = target
        self.timer = timer
        self.broadcast = broadcast
        self.loop = loop
        self.cancelable = cancelable
        self.dispatchers = dispatchers or []
        self.decorators = decorators or []
        self.enableInternalAccess = enableInternalAccess
        self.sleep_record = EnteredRecord()
        self.started_record = EnteredRecord()

    def setup_task(self) -> None:
        if not self.started_record.entered:  # 还未启动
            self.task = self.loop.create_task(self.run())
        else:
            raise AlreadyStarted("the scheduler task has been started!")

    def sleep_interval_generator(self) -> Generator[float, None, None]:
        for next_execute_time in self.timer:
            if self.stopped:
                return
            now = datetime.now()
            if next_execute_time >= now:
                yield (next_execute_time - now).total_seconds()

    def coroutine_generator(self) -> Generator[
        Tuple[
            Coroutine,
            bool,
            Optional[float]
        ],
        None,
        None
    ]:
        for sleep_interval in self.sleep_interval_generator():
            yield Sleep(sleep_interval), True, sleep_interval
            yield (self.broadcast.Executor(
                target=ExecTarget(
                    callable_=self.target,
                    inline_dispatchers=self.dispatchers,
                    headless_decorators=self.decorators,
                    enable_internal_access=self.enableInternalAccess
                ),
                event=SchedulerTaskExecute()
            ), False, None)

    @print_track_async
    async def run(self) -> None:
        logger: Logger = get_var('application').logger
        debug: bool = get_var('debug')
        for coroutine, waiting, sleep_interval in self.coroutine_generator():
            if waiting:  # 是否为 asyncio.sleep 的 coroutine
                with self.sleep_record:
                    try:
                        await coroutine
                    except CancelledError:
                        return
            else:  # 执行
                if self.cancelable:
                    try:
                        await coroutine
                    except CancelledError:
                        if self.cancelable:
                            return
                        raise
                    except Exception as e:
                        logger.error(f"Got an error: {e}")
                        if debug:
                            print_exc()
                else:
                    try:
                        await Shield(coroutine)
                    except Exception as e:
                        logger.error(f"Got an error: {e}")
                        if debug:
                            print_exc()

    def stop_interval_gen(self) -> None:
        if not self.stopped:
            self.stopped = True

    async def join(self, stop=False):
        if stop and not self.stopped:
            self.stop_interval_gen()

        if self.task:
            await self.task

    def stop(self):
        if not self.task.cancelled():
            self.task.cancel()
