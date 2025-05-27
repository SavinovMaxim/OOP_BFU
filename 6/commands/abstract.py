from abc import ABC, abstractmethod


class Command(ABC):

    @property
    @abstractmethod
    def save_data(self) -> dict:
        ...

    @abstractmethod
    def execute(self) -> None:
        ...

    @abstractmethod
    def undo(self) -> None:
        ...
