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
from ujson import loads

from utils.typing import PathType


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


def load_config(config_file: PathType = 'config.yml',
                home_path: PathType = get_project_path()) -> dict:
    home = Path(home_path) if isinstance(home_path, str) else home_path
    if home.exists() and home.is_dir():

        path = home_path.joinpath(config_file) if isinstance(config_file, str) \
            else config_file
        if path.exists() and path.is_file() and path.suffix == '.yml':
            return YAML(typ='safe').load(path.open(encoding='utf-8'))
        else:
            raise FileExistsError(str(path))
    else:
        raise FileExistsError(str(home_path))


_config_ = load_config('config.yml')


def get_bot_config(config_var_name: str = None) -> dict:
    return _config_[config_var_name] if config_var_name else _config_


def refresh_bot_config() -> dict:
    global _config_
    _config_ = load_config('config.yml')
    return _config_


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


class JsonDict(dict):
    def __getattr__(self, item):
        return self.get(item)

    def __setattr__(self, key, value):
        self[key] = value


def JsonLoader(string: str, is_json_dict: bool = False, **kwargs):
    def to_json_dict(obj_):
        result = obj_
        if isinstance(result, dict):
            for key in result:
                result.update({
                    key: to_json_dict(result[key])
                })
            return JsonDict(result)
        elif isinstance(result, list):
            for item in result:
                index = result.index(item)
                result[index] = to_json_dict(item)
            return result
        elif isinstance(result, str):
            try:
                result = loads(result, **kwargs)
                return to_json_dict(result)
            except ValueError:
                return result
        return result

    return to_json_dict(string) if is_json_dict else loads(string, **kwargs)


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
