from typing import (
    List,
    Union,
)
from core.application.message.elements import (
    ExternalElement,
    InternalElement,
)
from core.application.message.elements.internal import Plain
from regex import split as re_split, match as re_match
from pydantic import validate_arguments
from core.application import MessageChain

ElementType = Union[InternalElement, ExternalElement]


def list_get(list_, index, default=None):
    if len(list_) - 1 >= index:
        return list_[index]
    return default


class Template:
    template: str

    def __init__(self, template_: str) -> None:
        self.template = template_

    def split_template(self) -> List[str]:
        return re_split(
                r"(?|(\$[a-zA-Z_][a-zA-Z0-9_]*)|(\$[0-9]*))",
                self.template
        )

    @validate_arguments
    def render(self,
               *args: Union[InternalElement, ExternalElement],
               **kwargs: Union[
                   InternalElement, ExternalElement]) -> MessageChain:
        patterns = []
        for pattern in self.split_template():
            if pattern:
                if not pattern.startswith("$"):
                    patterns.append(Plain(pattern))
                else:
                    if re_match(r"\$[a-zA-Z_][a-zA-Z0-9_]*", pattern):
                        patterns.append(kwargs.get(pattern[1:], Plain(pattern)))
                    elif re_match(r"\$[0-9]*", pattern):
                        patterns.append(list_get(args, int(pattern[1:])))
        return MessageChain.create(patterns)


def template(string: str, *args: ElementType, **kwargs: ElementType):
    return Template(template_=string).render(*args, **kwargs)
