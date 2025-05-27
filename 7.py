from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum
from inspect import signature, isclass
from typing import Type, Any, Optional, Callable, Union


class LifeStyle(Enum):
    PER_REQUEST = 'PerRequest'
    SCOPED = 'Scoped'
    SINGLETON = 'Singleton'


class Injector:
    _registry: dict[Type, tuple[Union[Type, Callable], LifeStyle, dict]]
    _singletons: dict[Type, Any]

    def __init__(self):
        self._registry = {}
        self._singletons = {}
        self._scoped_instances: Optional[dict[Type, Any]] = None

    def register(
            self,
            interface: Type,
            implementation: Union[Type, Callable],
            lifestyle: LifeStyle = LifeStyle.PER_REQUEST,
            params: Optional[dict] = None
    ):
        self._registry[interface] = (implementation, lifestyle, params or {})

    def get_instance(self, interface: Type) -> Any:
        impl, lifestyle, params = self._registry[interface]

        if lifestyle == LifeStyle.SINGLETON:
            if interface not in self._singletons:
                self._singletons[interface] = self._build(impl, params)
            return self._singletons[interface]

        if lifestyle == LifeStyle.SCOPED:
            if self._scoped_instances is None:
                raise RuntimeError('No active scope')
            if interface not in self._scoped_instances:
                self._scoped_instances[interface] = self._build(impl, params)
            return self._scoped_instances[interface]

        return self._build(impl, params)

    def _build(self, impl: Union[Type, Callable], params: dict) -> Any:
        if callable(impl) and not isclass(impl):
            return impl()

        ctor_params = {}
        sig = signature(impl.__init__)
        for name, param in sig.parameters.items():
            if param.annotation in self._registry:
                ctor_params[name] = self.get_instance(param.annotation)
        ctor_params.update(params)
        return impl(**ctor_params)

    @contextmanager
    def create_scope(self):
        previous = self._scoped_instances
        self._scoped_instances = {}
        try:
            yield
        finally:
            self._scoped_instances = previous

class IServiceA(ABC):
    @abstractmethod
    def do_a(self) -> str:
        pass


class IServiceB(ABC):
    @abstractmethod
    def do_b(self) -> str:
        pass


class IServiceC(ABC):
    @abstractmethod
    def do_c(self) -> str:
        pass


class ServiceADebug(IServiceA):
    def do_a(self) -> str:
        return 'A debug'


class ServiceARelease(IServiceA):
    def do_a(self) -> str:
        return 'A release'


class ServiceBDebug(IServiceB):
    def __init__(self, a_service: IServiceA):
        self._a = a_service

    def do_b(self) -> str:
        return f'B debug uses {self._a.do_a()}'


class ServiceBRelease(IServiceB):
    def __init__(self, a_service: IServiceA):
        self._a = a_service

    def do_b(self) -> str:
        return f'B release uses {self._a.do_a()}'


class ServiceCDebug(IServiceC):
    def __init__(self, b_service: IServiceB):
        self._b = b_service

    def do_c(self) -> str:
        return f'C debug uses {self._b.do_b()}'


class ServiceCRelease(IServiceC):
    def __init__(self, b_service: IServiceB):
        self._b = b_service

    def do_c(self) -> str:
        return f'C release uses {self._b.do_b()}'


# ===== Configuration 1 =====
config1 = Injector()
config1.register(IServiceA, ServiceADebug, LifeStyle.PER_REQUEST)
config1.register(IServiceB, ServiceBDebug, LifeStyle.SCOPED)
config1.register(IServiceC, ServiceCDebug, LifeStyle.SINGLETON)

# ===== Configuration 2 =====
config2 = Injector()
config2.register(IServiceA, ServiceARelease, LifeStyle.SINGLETON)
config2.register(IServiceB, ServiceBRelease, LifeStyle.PER_REQUEST)
config2.register(
    IServiceC,
    lambda: ServiceCRelease(config2.get_instance(IServiceB)),
    LifeStyle.PER_REQUEST
)


# ===== Demonstration =====
def demo(injector: Injector):
    print('---- New Request ----')
    a1 = injector.get_instance(IServiceA)
    a2 = injector.get_instance(IServiceA)
    print(f'A? {a1 is a2}')

    with injector.create_scope():
        b1 = injector.get_instance(IServiceB)
        b2 = injector.get_instance(IServiceB)
        print(f'B in scope? {b1 is b2}')

        c1 = injector.get_instance(IServiceC)
        c2 = injector.get_instance(IServiceC)
        print(f'C? {c1 is c2}')

        print(a1.do_a(), b1.do_b(), c1.do_c(), sep=' | ')


if __name__ == '__main__':
    print('== Config 1 ==')
    demo(config1)

    print('\n== Config 2 ==')
    demo(config2)
