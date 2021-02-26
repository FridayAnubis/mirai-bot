from abc import (
    ABC,
    abstractmethod,
)
from sys import stderr
from typing import Union
from pathlib import Path

from loguru import logger as _Logger

from .. import get_config


class AbstractLogger(ABC):
    @abstractmethod
    def info(self, msg):
        ...

    @abstractmethod
    def error(self, msg):
        ...

    @abstractmethod
    def debug(self, msg):
        ...

    @abstractmethod
    def warn(self, msg):
        ...

    @abstractmethod
    def plugin(self, msg):
        ...

    @abstractmethod
    def exception(self, msg):
        ...

    @abstractmethod
    def bot(self, msg, **kwargs):
        ...

    @abstractmethod
    def success(self, msg):
        pass


class Logger(AbstractLogger):
    __logger: _Logger

    def __init__(self) -> None:
        debug: bool = get_config('debug')
        self.__logger = _Logger
        # {thread.name} {file}:{module}.{function} {line}|
        time_fmt = "{time:HH:mm:ss}"  # {time:YYYY-MM-DD HH:mm:ss.SSS}
        fmt = "|<green>" \
              + time_fmt \
              + "</green>|<level>{level.icon}</level>|<level>{message}</level>"
        self.__logger.remove()
        self.__logger.add(
            stderr,
            format=fmt,
            enqueue=False,
            level=10 if debug else 0
        )
        try:
            self.__logger.level("DEBUG ", no=10, color="<light-black>",
                                icon="💡")
            self.__logger.level("INFO ", no=15, color="<fg #FFFFFF>", icon="  ")
            self.__logger.level("GROUP", no=15, color="<g>", icon="👪")
            self.__logger.level("FRIEND", no=15, color="<g>", icon="🙎")  # →←⇨⇦
            self.__logger.level("TEMP", no=15, color="<g>", icon="👤")
            self.__logger.level("PLUGIN", no=20, color="<c>", icon="🧩")
            self.__logger.level("SUCCESS ", no=25, color="<g><b>", icon="✔️")
            self.__logger.level("WARNING ", no=30, color="<y><b>", icon="⚠️")
            self.__logger.level("ERROR ", no=35, color="<r><b>", icon="❌")
            self.__logger.level("CRITICAL ", no=40, color="<fg #FC3F3F><b>",
                                icon="☠️")
            self.__logger.level("ORDER ", no=15, color="<light-black>",
                                icon="👉")
        except TypeError:
            ...

    def log_to_file(self, path: Union[str, Path] = None):
        from os import environ
        project_path = Path(environ.get('PROJECT_PATH'))
        config = get_config('log')

        log_path = project_path.joinpath(
            config['sink'] if path is None else path
        ).resolve()

        if not all([log_path.exists(), log_path.is_dir()]):
            self.warn(f"'{log_path}' does not exist.")
            log_path.mkdir()

        config.pop('sink')
        self.__logger.add(
            sink=f"{log_path.__str__()}/file.log",
            level=10,
            **config
        )

    def debug(self, msg):
        return self.__logger.log("DEBUG ", msg)

    def info(self, msg):
        return self.__logger.log("INFO ", msg)

    def plugin(self, msg):
        return self.__logger.log("PLUGIN", msg)

    def success(self, msg):
        return self.__logger.log("SUCCESS ", msg)

    def warn(self, msg):
        return self.__logger.log("WARNING ", msg)

    def error(self, msg):
        return self.__logger.log("ERROR ", msg)

    def exception(self, msg):
        return self.__logger.exception(msg)

    def critical(self, msg):
        return self.__logger.log("CRITICAL ", msg)

    def bot(self, msg, **kwargs):
        def cut_length(string: str, length: int, fillChar: str = ' ') -> str:
            string = str(string)
            real_len = 0
            chinese_n = 0
            char_n = 0
            for char in string:
                is_chinese = len(char.encode('utf-8')) == 3
                chinese_n += 1 if is_chinese else 0
                real_len += 2 if is_chinese else 1
                char_n += 1
                if real_len > length:
                    char_n -= 1 if is_chinese else 0
                    return string[:char_n] + '.' * (real_len - length + 2)
            return string.center(length - chinese_n, fillChar)

        receive = kwargs.get('receive')
        message_type = kwargs.get('type')
        target = kwargs.get('target')
        header = '{}({}) '.format(
            cut_length(target.group.name, 12),
            cut_length(target.group.id, 9)
        ) if any([
            all([receive, message_type == 'group']),
            message_type == 'temp']
        ) else ''
        level = "GROUP" if message_type == 'group' else (
            'FRIEND' if message_type == 'friend' else 'TEMP')
        try:
            return self.__logger.opt(colors=True, capture=True).log(
                level,
                f"<light-blue>{header}</>" +
                f"<light-cyan>{target.name}({target.id})</> <light-red>" +
                ("->" if receive else "<-") + "</> " + msg
            )
        except Exception as e:
            print(receive, message_type, target)
            raise e

    def order(self, name, msg):
        return self.__logger.opt(colors=True) \
            .log("ORDER ", f"<light-cyan>{name}</>:<g>{msg}</>")
