from core.broadcast import BaseDispatcher
from pydantic import (
    validator,
)
from core.broadcast import BaseEvent
from core.application.context import application
from core.application.exceptions import InvalidEventTypeDefinition


class MiraiEvent(BaseEvent):
    __base_event__ = True
    type: str

    @validator("type")
    def type_limit(cls, v):
        if cls.type != v:
            raise InvalidEventTypeDefinition(
                "{0}'s type must be '{1}', not '{2}'".format(cls.__name__,
                                                             cls.type, v)
            )
        return v

    class Config:
        extra = "ignore"

    class Dispatcher:
        pass


class ApplicationDispatcher(BaseDispatcher):
    @staticmethod
    def catch(interface):
        if getattr(interface.annotation, "__name__",
                   None) == "KarakoMiraiApplication":
            return application.get()


class EmptyDispatcher(BaseDispatcher):
    mixin = [ApplicationDispatcher]

    @staticmethod
    def catch(interface):
        pass


