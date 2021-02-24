from inspect import currentframe
from os import environ
from pathlib import Path
from typing import (
    Union,
    Any,
)

from ruamel.yaml import YAML as _YAML
from ruamel.yaml.compat import StringIO


def get_project_path() -> Path:
    project_path = environ.get('PROJECT_PATH')
    print()
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


def get_config(config_var_name: str = None) -> dict:
    return YAML(typ='safe').load(
        get_project_path()
            .joinpath("config.yml")
            .open(encoding='utf-8')
    )[config_var_name] if config_var_name else YAML(typ='safe').load(
        get_project_path()
            .joinpath("config.yml")
            .open(encoding='utf-8')
    )


def get_var_name(var: Any) -> Union[str, None]:
    callers_local_vars = currentframe().f_back.f_locals.items()
    for var_name, var_val in callers_local_vars:
        if var_val is var:
            return var_name
    return None
