from typing import Any

from core.broadcast.entities.dispatcher import BaseDispatcher
from core.broadcast.entities.event import BaseEvent
from core.broadcast.interfaces.dispatcher import DispatcherInterface


class ApplicationLaunched(BaseEvent):
    app: Any

    def __init__(self, app) -> None:
        super().__init__(app=app)

    class Dispatcher(BaseDispatcher):
        @staticmethod
        def catch(interface: "DispatcherInterface"):
            from .. import KarakoMiraiApplication

            if interface.annotation is KarakoMiraiApplication:
                return interface.event.app


class ApplicationLaunchedBlocking(BaseEvent):
    app: Any

    def __init__(self, app) -> None:
        super().__init__(app=app)

    class Dispatcher(BaseDispatcher):
        @staticmethod
        def catch(interface: "DispatcherInterface"):
            from .. import KarakoMiraiApplication

            if interface.annotation is KarakoMiraiApplication:
                return interface.event.app


class ApplicationShutdown(BaseEvent):
    app: Any

    def __init__(self, app) -> None:
        super().__init__(app=app)

    class Dispatcher(BaseDispatcher):
        @staticmethod
        def catch(interface: "DispatcherInterface"):
            from .. import KarakoMiraiApplication

            if interface.annotation is KarakoMiraiApplication:
                return interface.event.app
