from abc import ABC, abstractmethod


class IBaseService(ABC):
    @abstractmethod
    def name(self) -> str:
        """Return the name of the service."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if the service is healthy, False otherwise."""
        pass


class IDIService(IBaseService):
    @abstractmethod
    def register_dependency(self, dep: object) -> None:
        """Register a dependency with the DI service."""
        pass

    @abstractmethod
    def resolve(self, name: str) -> object:
        """Resolve a dependency by name."""
        pass

    # Add more abstract methods as needed for DI test scenarios


class IServiceA(ABC):
    @abstractmethod
    def do_a(self):
        pass


class IServiceB(ABC):
    @abstractmethod
    def do_b(self):
        pass


class IServiceC(ABC):
    @abstractmethod
    def do_c(self):
        pass
