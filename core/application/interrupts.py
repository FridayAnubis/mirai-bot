from typing import (
    Callable,
    Optional,
    Union,
)
from core.broadcast.exceptions import ExecutionStop
from core.broadcast.interrupt.waiter import Waiter
from core.application import (
    Group,
    Member,
)
from core.application import (
    Quote,
    Source,
)
from core.application import BotMessage
from core.application import (
    FriendMessage,
    GroupMessage,
    TempMessage,
)
from core.application import Friend


def GroupMessageInterrupt(
        special_group: Optional[Union[Group, int]] = None,
        special_member: Optional[Union[Member, int]] = None,
        quote_access: Optional[Union[BotMessage, Source]] = None,
        custom_judgement: Optional[Callable[[GroupMessage], bool]] = None,
        block_propagation: bool = False,
):
    @Waiter.create_using_function(
            [GroupMessage],
            block_propagation=block_propagation)
    def GroupMessageInterruptWaiter(event: GroupMessage):
        if special_group:
            if event.sender.group.id != (
                    special_group.id if isinstance(special_group,
                                                   Group) else special_group
            ):
                raise ExecutionStop()
        if special_member:
            if event.sender.id != (
                    special_member.id
                    if isinstance(special_member, Member)
                    else special_member
            ):
                raise ExecutionStop()
        if quote_access:
            quotes = event.messageChain.get(Quote)
            if not quotes:
                raise ExecutionStop()
            quote: Quote = quotes[0]
            if isinstance(quote_access, BotMessage):
                if quote.id != quote_access.messageId:
                    raise ExecutionStop()
            elif isinstance(quote_access, Source):
                if quote.id != quote_access.id:
                    raise ExecutionStop()
        if custom_judgement:
            if not custom_judgement(event):
                raise ExecutionStop()
        return event

    return GroupMessageInterruptWaiter


def FriendMessageInterrupt(
        special_friend: Optional[Union[Friend, int]] = None,
        quote_access: Optional[Union[BotMessage, Source]] = None,
        custom_judgement: Optional[Callable[[FriendMessage], bool]] = None,
        block_propagation: bool = False,
):
    @Waiter.create_using_function([FriendMessage],
                                  block_propagation=block_propagation)
    def FriendMessageInterruptWaiter(event: FriendMessage):
        if special_friend:
            if event.sender.id != (
                    special_friend.id
                    if isinstance(special_friend, Friend)
                    else special_friend
            ):
                raise ExecutionStop()
        if quote_access:
            quotes = event.messageChain.get(Quote)
            if not quotes:
                raise ExecutionStop()
            quote: Quote = quotes[0]
            if isinstance(quote_access, BotMessage):
                if quote.id != quote_access.messageId:
                    raise ExecutionStop()
            elif isinstance(quote_access, Source):
                if quote.id != quote_access.id:
                    raise ExecutionStop()
        if custom_judgement:
            if not custom_judgement(event):
                raise ExecutionStop()
        return event

    return FriendMessageInterruptWaiter


def TempMessageInterrupt(
        special_group: Optional[Union[Group, int]] = None,
        special_member: Optional[Union[Member, int]] = None,
        quote_access: Optional[Union[BotMessage, Source]] = None,
        custom_judgement: Optional[Callable[[TempMessage], bool]] = None,
        block_propagation: bool = False,
):
    @Waiter.create_using_function([TempMessage],
                                  block_propagation=block_propagation)
    def TempMessageInterruptWaiter(event: TempMessage):
        if special_group:
            if event.sender.group.id != (
                    special_group.id if isinstance(special_group,
                                                   Group) else special_group
            ):
                raise ExecutionStop()
        if special_member:
            if event.sender.id != (
                    special_member.id
                    if isinstance(special_member, Member)
                    else special_member
            ):
                raise ExecutionStop()
        if quote_access:
            quotes = event.messageChain.get(Quote)
            if not quotes:
                raise ExecutionStop()
            quote: Quote = quotes[0]
            if isinstance(quote_access, BotMessage):
                if quote.id != quote_access.messageId:
                    raise ExecutionStop()
            elif isinstance(quote_access, Source):
                if quote.id != quote_access.id:
                    raise ExecutionStop()
        if custom_judgement:
            if not custom_judgement(event):
                raise ExecutionStop()
        return event

    return TempMessageInterruptWaiter
