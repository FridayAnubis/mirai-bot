from abc import (
    abstractmethod,
    ABC,
)
from typing import Any

from pydantic import BaseModel


class Element(BaseModel):
    def asSerializationString(self):
        ...

    def asDisplay(self):
        ...


class InternalElement(Element, ABC):
    def toExternal(self, *args, **kwargs) -> "ExternalElement":
        """可以为异步方法"""
        pass

    @classmethod
    @abstractmethod
    def fromExternal(cls, external_element) -> "InternalElement":
        """可以为异步方法"""
        pass

    def asDisplay(self) -> str:
        return ""

    def asSerializationString(self) -> str:
        return ""


class ExternalElement(Element):
    pass


class ShadowElement(Element):
    pass


def isShadowElement(any_instance: Any) -> bool:
    """检查实例是否为 Shadow Element

    Args:
        any_instance (Any): 欲检查的实例

    Returns:
        bool: 是否为 Shadow Element
    """
    return isinstance(any_instance, ShadowElement)
