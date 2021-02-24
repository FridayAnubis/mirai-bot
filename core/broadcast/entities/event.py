from iterwrapper import IterWrapper
from pydantic.main import (
    BaseModel,
    ModelMetaclass,
)


class EventMeta(ModelMetaclass):
    def __new__(mcs, name, bases, mapping, **kwargs):
        if any(
                IterWrapper(bases)
                        .filter(lambda x: getattr(x, "__base_event__", False))
                        .collect(list)
        ):
            if not mapping.__contains__("__base_event__"):
                mapping["__base_event__"] = False
        if not mapping.get("Dispatcher") and name != "BaseEvent":
            raise AttributeError(
                    "a event class must have a dispatcher called 'Dispatcher'"
            )
        r = super().__new__(
                mcs,
                name,
                (BaseModel, *bases) if name == "BaseEvent" else bases,
                mapping,
                **kwargs
        )
        if mapping.get("type"):
            r.type = mapping.get("type")
        if name != "BaseEvent":
            r.update_forward_refs()
            r.Dispatcher = mapping["Dispatcher"]
        return r


class BaseEvent(metaclass=EventMeta):
    class Config:
        arbitrary_types_allowed = True


