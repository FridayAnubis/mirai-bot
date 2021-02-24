
from ..friend import Friend
from ..group_ import (
    Member,
    Group,
)
from ..message.chain import MessageChain
from core.broadcast import BaseDispatcher
from core.broadcast.interfaces.dispatcher import DispatcherInterface
from . import (
    ApplicationDispatcher,
    MiraiEvent,
)
from .dispatcher import MessageChainCatcher


class FriendMessage(MiraiEvent):
    type: str = "FriendMessage"
    messageChain: MessageChain
    sender: Friend

    class Dispatcher(BaseDispatcher):
        mixin = [MessageChainCatcher, ApplicationDispatcher]

        @staticmethod
        def catch(interface: DispatcherInterface):
            if interface.annotation is Friend:
                return interface.event.sender


class GroupMessage(MiraiEvent):
    type: str = "GroupMessage"
    messageChain: MessageChain
    sender: Member

    class Dispatcher(BaseDispatcher):
        mixin = [MessageChainCatcher, ApplicationDispatcher]

        @staticmethod
        def catch(interface: DispatcherInterface):
            if interface.annotation is Group:
                return interface.event.sender.group
            elif interface.annotation is Member:
                return interface.event.sender


class TempMessage(MiraiEvent):
    type: str = "TempMessage"
    messageChain: MessageChain
    sender: Member

    @classmethod
    def parse_obj(cls, obj):
        return super().parse_obj(obj)

    class Dispatcher(BaseDispatcher):
        mixin = [MessageChainCatcher, ApplicationDispatcher]

        @staticmethod
        def catch(interface: DispatcherInterface):
            if interface.annotation is Group:
                return interface.event.sender.group
            elif interface.annotation is Member:
                return interface.event.sender
