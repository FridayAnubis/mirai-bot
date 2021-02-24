import asyncio

from core.scheduler import KarakoScheduler
from core.scheduler.timers import (
    every_minute,
    crontabify,
)
from core.scheduler.task import SchedulerTask
from core.broadcast import Broadcast

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
scheduler = KarakoScheduler(loop, bcc)


async def nothing():
    ...


@scheduler.schedule(every_minute())
async def test():
    for _ in range(20):
        task = SchedulerTask(
            target=nothing,
            timer=crontabify('1 1 1 1 *'),
            broadcast=bcc,
            loop=loop
        )
        scheduler.addSchedule(task)
        task.setup_task()
