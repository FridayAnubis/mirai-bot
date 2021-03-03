from inspect import currentframe
from os import environ
from pathlib import Path
from random import randint
from typing import (
    Union,
    Any,
)

from ruamel.yaml import YAML as _YAML
from ruamel.yaml.compat import StringIO


def get_project_path() -> Path:
    project_path = environ.get('PROJECT_PATH')
    if not project_path:
        project_path = Path(__file__).parent.parent
        environ.setdefault(
            'PROJECT_PATH',
            str(project_path.resolve())
        )
    return Path(project_path) if isinstance(project_path, str) else project_path


class YAML(_YAML):
    def dump(self, data, stream=None, **kwargs):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        # elif isinstance(stream, Path):
        #     stream =
        _YAML.dump(self, data, stream, **kwargs)
        if inefficient:
            return stream.getvalue()


_config_ = YAML(typ='safe').load(
    get_project_path()
        .joinpath("config.yml")
        .open(encoding='utf-8')
)


def get_config(config_var_name: str = None) -> dict:
    return _config_[config_var_name] if config_var_name else _config_


def get_var_name(var: Any) -> Union[str, None]:
    callers_local_vars = currentframe().f_back.f_locals.items()
    for var_name, var_val in callers_local_vars:
        if var_val is var:
            return var_name
    return None


def format_time(time_: float, c: str = '') -> str:
    if time_ == 0:
        return '0μs'
    __time = time_
    h = int(__time // (60 * 60))
    __time = __time % (60 * 60)

    m = int(__time // 60)
    __time = __time % 60

    s = int(__time // 1)
    __time = (__time - s) * 1000

    ms = int(__time // 1)
    __time = (__time - ms) * 1000

    us = round(__time // 1, 2)
    us = int(us) if us == int(us) else us

    result = [
        f"{h}h" if h != 0 else "",
        f"{m}m" if m != 0 else "",
        f"{s}s" if s != 0 else "",
        f"{ms}ms" if ms != 0 else "",
        f"{us}μs" if us != 0 else ""
    ]

    return c.join([i for i in result if i != ""])


def serial_number(num: int, serial_type: int = 0) -> str:
    if num is None:
        return num
    result_list = [
        "①②③④⑤⑥⑦⑧⑨⑩",
        "㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩",
        "⒈⒉⒊⒋⒌⒍⒎⒏⒐⒑⒒⒓⒔⒕⒖⒗⒘⒙⒚⒛",
        "⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿⒀⒁⒂⒃⒄⒅⒆⒇",
        "ⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹ",
        "ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ"
    ]
    result_list_len = [len(i) for i in result_list]
    result_list_max_len = max(result_list_len)
    if num - 1 > result_list_max_len:
        return None
    elif result_list_len[serial_type] < num:
        serial_type = randint(2, 3)
    return result_list[serial_type][num - 1]
