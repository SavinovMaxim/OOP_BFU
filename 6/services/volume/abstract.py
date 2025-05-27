from abc import abstractmethod, ABC


class AbstractVolumeService(ABC):
    @abstractmethod
    def increase_volume(self, value: int):
        """Уеличить звук"""
        ...

    @abstractmethod
    def decrease_volume(self, value: int):
        """Уменьшить"""
        ...
