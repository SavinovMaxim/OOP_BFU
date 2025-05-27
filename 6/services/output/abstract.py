from abc import abstractmethod, ABC


class AbstractOutputService(ABC):
    @abstractmethod
    def char(self, char: str) -> None:
        """Вывод литералов"""
        ...

    def message(self, message: str, *kwargs) -> None:
        """Вывод целого сообщения"""
        ...

    @abstractmethod
    def remove_last_char(self) -> None:
        """Удалить ласт чар - для undo"""
        ...

