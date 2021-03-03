import sys
from asyncio import sleep as Sleep
from importlib import import_module
from pathlib import Path
from types import (
    ModuleType,
    FunctionType,
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
    ExecTarget,
    DispatcherInterface,
    UnExistedNamespace,
)
from core.broadcast.utilles import cached_isinstance
from core.scheduler import SchedulerTask
from utils.context import get_var
from utils.typing import (
    Timer,
    PathType,
    Optional,
    Union,
    Type,
    List,
)

bot = get_var('bot')
application: "KarakoMiraiApplication" = bot.application
scheduler: "KarakoScheduler" = bot.scheduler
broadcast = application.broadcast
loop = broadcast.loop


def feature(
        event: Union[str, Type[BaseEvent]],
        *,
        priority: int = 16,
        namespace: Namespace = None,
        decorators: Union[List[Decorator], Decorator] = None,
        dispatchers: Union[List[BaseDispatcher], BaseDispatcher] = None,
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
    decorators = list(decorators) if not isinstance(decorators, list) \
        else decorators
    dispatchers = [dispatchers] if not isinstance(dispatchers, list) \
        else dispatchers

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
        self._module = import_module(self._module_path)
        if self._status:
            self._status = False
            self.turn_on()

    def uninstall(self):
        try:
            application.broadcast.removeNamespace(
                    self._module.__name__.split('.')[-1]
            )
        except UnExistedNamespace:
            pass
        sys.modules.pop(self._module.__name__)
        self._module.__dict__.clear()
        self._module = None
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
    def cube_paths(cls) -> List[PathType]:
        result = []
        home = Path(__file__).parent
        for cube_path in home.iterdir():
            if any([
                all([
                    cube_path.is_file(),
                    not cube_path.name.startswith('_'),
                    cube_path.suffix == '.py',
                    cube_path.stem != '__base__'
                ]),
                all([
                    cube_path.is_dir(),
                    cube_path.joinpath('__init__.py').exists()
                ])
            ]):
                result.append(f'{home.name}.{cube_path.stem}')
        return result

    @classmethod
    def load_form_path(cls, cube_path) -> "Cube":
        try:
            module = import_module(cube_path)
        except Exception as e:
            application.logger.exception(
                    f"An error occurred while loading the "
                    f"cube({cube_path}): {e}"
            )
            raise e
        return cls(module)

    @classmethod
    async def scan_load(cls):

        class CubeLoadTaskExecute(BaseEvent):
            class Dispatcher(BaseDispatcher):
                def catch(self: DispatcherInterface):
                    ...

        def cube_module_path_list():
            return [_._module_path for _ in cls.__cube_list__]

        def scan():
            for cube_path in cls.cube_paths():
                if cube_path not in cube_module_path_list():
                    application.logger.info(
                            f'Detect a cube from "{cube_path}"'
                    )
                    try:
                        cube = cls.load_form_path(cube_path)
                        application.logger.success(
                                f"The cube named '{cube._name}' has been loaded."
                        )
                    except Exception as e:
                        application.logger.debug(f'cube load error:{e}')
                        continue
                    cube.install()
                    cls.__cube_list__.append(cube)
                    if not cube.__getattribute__('_disable'):
                        cube.turn_on()
            for cube_path in cube_module_path_list():
                if cube_path not in cls.cube_paths():
                    application.logger.warn(
                            f"The cube from '{cube_path}' has been deleted."
                    )
                    try:
                        cube = cls.get_by_module_path(cube_path)
                        cube.turn_off()
                        cube.uninstall()
                        application.logger.success(
                                f"The cube named '{cube._name}' has been "
                                f"uninstalled."
                        )
                    except Exception as e:
                        application.logger.exception(e)
                        continue

        def coroutine_generator():
            while True:
                yield Sleep(0)
                yield broadcast.Executor(
                        target=ExecTarget(
                                callable_=scan,
                                inline_dispatchers=[],
                                headless_decorators=[],
                                enable_internal_access=False
                        ),
                        event=CubeLoadTaskExecute()
                )

        for coroutine in coroutine_generator():
            await coroutine

    @classmethod
    def initialize(cls):
        home = Path(__file__).parent
        path = home.joinpath('__base__.py')
        module_path = f'{home.name}.{path.stem}'
        cube = cls.load_form_path(module_path)
        cube.install()
        cube.turn_on()
        loop.create_task(cls.scan_load())

    @classmethod
    def get_by_name(cls, cube_name: str) -> "Cube":
        for cube in cls.__cube_list__:
            if cube.name == cube_name:
                return cube
        return None

    @classmethod
    def get_by_module_path(cls, module_path: str) -> "Cube":
        for cube in cls.__cube_list__:
            if cube._module_path == module_path:
                return cube
