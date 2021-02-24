import sys
from importlib import (
    reload as reload_module,
    import_module,
)
from pathlib import Path
from time import time
from types import (
    ModuleType,
    FunctionType,
)
from typing import (
    Optional,
    Union,
    Type,
    List,
)

from core import KarakoMiraiApplication
from core.broadcast import (
    BaseEvent,
    Namespace,
    Decorator,
    BaseDispatcher,
    InvalidEventName,
    Listener,
    RegisteredEventListener,
)
from core.broadcast.utilles import cached_isinstance
from utils import format_time
from utils.context import get_var

application: "KarakoMiraiApplication" = get_var('application')
broadcast = application.broadcast


def feature(
        event: Union[str, Type[BaseEvent]],
        *,
        priority: int = 16,
        dispatchers: List[BaseDispatcher] = None,
        namespace: Namespace = None,
        decorators: List[Decorator] = None,
        enable_internal_access: bool = False,
):
    dispatchers = [] if dispatchers is None else dispatchers
    decorators = [] if decorators is None else decorators
    if cached_isinstance(event, str):
        name = event
        event = broadcast.findEvent(event)
        if not event:
            raise InvalidEventName(name, 'is not valid!')
    priority = (type(priority) == int) and priority or int(priority)

    def feature_wrapper(callable_target: FunctionType):
        result = broadcast.getListener(callable_target)
        namespace_ = broadcast.createNamespace(
            callable_target.__module__.split('.')[-1], hide=True
        ) if namespace is None else namespace
        if result is None:
            broadcast.addListener(
                Listener(
                    callable_=callable_target,
                    namespace=namespace_,
                    inline_dispatchers=dispatchers,
                    priority=priority,
                    listening_events=[event],
                    headless_decorators=decorators,
                    enable_internal_access=enable_internal_access
                )
            )
        else:
            if event not in result:
                result.listening_events.append(event)
            else:
                raise RegisteredEventListener(
                    event.__name__, "has been registered!"
                )

        return callable_target

    return feature_wrapper


class Cube:
    __cube_list__: List["Cube"] = []

    _module: ModuleType = None
    _module_path: str

    _status: bool = False

    _name: str
    _author: str
    _description: Optional[str]

    def __init__(self, module: Union[str, ModuleType]):
        if isinstance(module, ModuleType):
            self._module = module
            self._module_path = self._module.__name__
        else:
            self._module_path = module
            try:
                self._module = import_module(self._module_path)
            except Exception as e:
                application.logger.exception(
                    f"An error occurred while loading the cube "
                    f"'{self._module_path}': {e}"
                )
                raise e

        try:
            self._name = self._module.__getattribute__('_name')
        except AttributeError:
            raise AttributeError(
                f'Cube "{self._module_path}" has no "_name" attribute.'
            )
        try:
            self._author = self._module.__getattribute__('_author')
        except AttributeError:
            raise AttributeError(
                f'Cube "{self._module_path}" has no "_author" attribute.'
            )
        try:
            self._description = self._module.__getattribute__('_description')
        except AttributeError:
            ...

    def install(self):
        module = import_module(self._module_path)
        self._module = module

    def reinstall(self):
        for var in [_ for _ in dir(self._module) if not _.startswith('__')]:
            eval(f'del {self._module.__name__}.{var}')
        application.broadcast.removeNamespace(
            self._module.__name__.split('.')[-1]
        )
        reload_module(self._module)

    def uninstall(self):
        sys.modules.pop(self._module.__name__)
        self._module = None
        application.broadcast.removeNamespace(
            self._module.__name__.split('.')[-1]
        )
        Cube.__cube_list__.remove(self)

    def turn_on(self):
        if not self._status:
            application.broadcast.unHideNamespace(
                self._module.__name__.split('.')[-1]
            )
            self._status = True

    def turn_off(self):
        if self._status:
            application.broadcast.hideNamespace(
                self._module.__name__.split('.')[-1]
            )

    @classmethod
    def initialize(cls):
        home = Path(__file__).parent
        path = home.joinpath('__base__.py')
        module_path = f'{home.name}.{path.stem}'
        try:
            module = import_module(module_path)
        except Exception as e:
            application.logger.exception(
                f"An error occurred while loading the base cube: {e}"
            )
            raise e
        cube = cls(module)
        cls.__cube_list__.append(cube)
        cube.install()

    @classmethod
    def install_all_cube(cls):
        success = 0
        fail = 0
        count = 0
        start_time = time()

        home = Path(__file__).parent
        for cube_path in home.iterdir():
            if any([
                not cube_path.name.startswith('_'),
                all([
                    cube_path.is_dir(),
                    cube_path.joinpath('__init__.py').exists()
                ])
            ]):
                count += 1
                module_path = f'{home.name}.{cube_path.stem}'
                try:
                    module = import_module(module_path)
                except Exception as e:
                    application.logger.exception(
                        f"An error occurred while loading the "
                        f"cube({module_path}): {e}"
                    )
                    fail += 1
                    continue
                cube = cls(module)
                cls.__cube_list__.append(cube)
                success += 1
        used_time = time() - start_time
        if count is success:
            application.logger.success(
                'All cubes are installed successfully, took {}'
                    .format(format_time(used_time, ' '))
            )
        else:
            application.logger.warn(
                "Success {} cubes, fail {} plugins.".format(success, fail)
            )
        return success, fail, count, start_time

    @classmethod
    def reinstall_all_cube(cls):
        for cube in cls.__cube_list__:
            cube.reinstall()

    @classmethod
    def uninstall_all_cube(cls):
        for cube in cls.__cube_list__:
            cube.uninstall()
