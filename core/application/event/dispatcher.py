from core.broadcast import BaseDispatcher
from core.broadcast.interfaces.dispatcher import DispatcherInterface
from ..message.chain import MessageChain


class MessageChainCatcher(BaseDispatcher):
    @staticmethod
    def catch(interface: "DispatcherInterface"):
        if interface.annotation is MessageChain:
            return interface.event.messageChain
