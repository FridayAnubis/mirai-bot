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

from core import (
    KarakoMiraiApplication,
    KarakoScheduler,
)
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
from core.scheduler import SchedulerTask
from utils import format_time
from utils.context import get_var
from utils.typing import Timer

bot = get_var('bot')
application: "KarakoMiraiApplication" = bot.application
scheduler: "KarakoScheduler" = bot.scheduler
broadcast = application.broadcast


def feature(
        event: Union[str, Type[BaseEvent]],
        *,
        priority: int = 16,
        namespace: Namespace = None,
        decorators: List[Decorator] = None,
        dispatchers: List[BaseDispatcher] = None,
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


def schedule(
        timer: Timer,
        *,
        cancelable: bool = True,
        decorators: List[Decorator] = None,
        dispatchers: List[BaseDispatcher] = None,
        enableInternalAccess: Optional[bool] = False
):
    def schedule_wrapper(func):
        task = SchedulerTask(
            func, timer, broadcast, broadcast.loop, cancelable,
            decorators, dispatchers, enableInternalAccess,
            scheduler.createNamespace(func.__module__.split('.')[-1])
        )
        scheduler.addSchedule(task)
        return func

    return schedule_wrapper


class Cube:
    __cube_list__: List["Cube"] = []

    _module: ModuleType = None
    _module_path: str

    _status: bool = False

    _disable: bool
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
            self._disable = self._module.__getattribute__('_disable')
        except AttributeError:
            raise AttributeError(
                f'Cube "{self._module_path}" has no "_disable" attribute.'
            )

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
        if self._status:
            self._status = False
            self.turn_on()

    def uninstall(self):
        sys.modules.pop(self._module.__name__)
        self._module = None
        application.broadcast.removeNamespace(
            self._module.__name__.split('.')[-1]
        )
        Cube.__cube_list__.remove(self)
        self._status = False

    def turn_on(self):
        if not self._status:
            application.broadcast.unHideNamespace(
                self._module.__name__.split('.')[-1]
            )
            scheduler.enableNamespace(self._module.__name__.split('.')[-1])
            self._status = True

    def turn_off(self):
        if self._status:
            application.broadcast.hideNamespace(
                self._module.__name__.split('.')[-1]
            )
            scheduler.disableNamespace(self._module.__name__.split('.')[-1])
            self._status = False

    def switch(self) -> bool:
        if self._status:
            self.turn_off()
        else:
            self.turn_on()
        self._status = not self._status
        return self._status

    @property
    def name(self):
        return self._name

    @property
    def author(self):
        return self._author

    @property
    def description(self):
        return self._description

    @property
    def is_disable(self):
        return self._disable

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
        cube.install()
        cube.turn_on()

    @classmethod
    def install_all_cube(cls):
        success = 0
        fail = 0
        count = 0
        start_time = time()

        home = Path(__file__).parent
        for cube_path in home.iterdir():
            if any([
                all([
                    cube_path.is_file(),
                    not cube_path.name.startswith('_'),
                    cube_path.suffix == '.py'
                ]),
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
                if not cube.__getattribute__('_disable'):
                    cube.turn_on()
                success += 1
        used_time = format_time(time() - start_time, ' ')
        if count is success:
            application.logger.success(
                'All cubes are installed successfully, took {}'
                    .format(used_time)
            )
        else:
            application.logger.warn(
                "Success {} cubes, fail {} plugins.".format(success, fail)
            )
        return success, fail, count, used_time

    @classmethod
    def reinstall_all_cube(cls):
        success = 0
        fail = 0
        count = 0
        start_time = time()
        for cube in cls.__cube_list__:
            count += 1
            try:
                cube.reinstall()
                success += 1
            except Exception as e:
                application.logger.error(
                    f"An error occurred while loading the "
                    f"cube({cube._module_path}): {e}"
                )
                fail += 1
        used_time = format_time(time() - start_time, ' ')
        return success, fail, count, used_time

    @classmethod
    def uninstall_all_cube(cls):
        success = 0
        fail = 0
        count = 0
        start_time = time()
        for cube in cls.__cube_list__:
            count += 1
            try:
                cube.uninstall()
                success += 1
            except Exception as e:
                application.logger.error(
                    f"An error occurred while loading the "
                    f"cube({cube._module_path}): {e}"
                )
                fail += 1
        used_time = format_time(time() - start_time, ' ')
        return success, fail, count, used_time
