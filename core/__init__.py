from asyncio import get_event_loop
from asyncio.windows_events import ProactorEventLoop
from os import environ
from pathlib import Path

from core.application import (
    KarakoMiraiApplication,
    Session,
)
from core.broadcast import Broadcast
from core.broadcast.interrupt import InterruptControl
from core.scheduler import KarakoScheduler
from utils import get_config
from utils.context import application
from utils.logger import (
    AbstractLogger,
    Logger,
)


class Bot:
    loop: ProactorEventLoop
    application: KarakoMiraiApplication
    session: Session
    broadcast: Broadcast
    scheduler: KarakoScheduler
    interrupt: InterruptControl
    logger: AbstractLogger

    def __init__(self, *, logger: AbstractLogger = None):
        self.config = get_config()

        self.loop = get_event_loop()
        self.logger = logger if logger else Logger()
        self.broadcast = Broadcast(loop=self.loop)
        self.scheduler = KarakoScheduler(self.loop, self.broadcast)
        self.session = Session(
            host=self.config['session']['host'],
            authKey=self.config['session']['authKey'],
            account=self.config['session']['account'],
            websocket=self.config['session']['websocket']
        )
        self.application = KarakoMiraiApplication(
            debug=self.config['debug'],
            broadcast=self.broadcast,
            connect_info=self.session,
            logger=self.logger
        )
        application.set(self.application)

    def run(self):
        if self.config['banner']:
            print(
                Path(
                    environ.get('PROJECT_PATH'))
                    .joinpath('resource/banner.txt')
                    .open(encoding='utf-8')
                    .read()
            )

        from cube import Cube
        if isinstance(self.logger, Logger):
            self.logger.log_to_file()
        Cube.initialize()
        del environ, Cube

        try:
            self.application.launch_blocking()
        except KeyboardInterrupt:
            self.logger.warn(f'{self.config["name"]} is closed.')
