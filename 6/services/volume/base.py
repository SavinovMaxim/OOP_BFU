from .abstract import AbstractVolumeService
from ..output.abstract import AbstractOutputService


class VolumeService(AbstractVolumeService):
    MAX_VALUE = 100
    MIN_VALUE = 0

    def __init__(self, output_service: AbstractOutputService, default_volume: int = 50):
        self._volume = default_volume
        self.__output_service = output_service

    def increase_volume(self, value: int) -> None:
        self._volume = min(self.MIN_VALUE, self._volume + value)
        message = f"volume increased +{value}%"
        self.__output_service.message(message)

    def decrease_volume(self, value: int) -> None:
        self._volume = max(self.MAX_VALUE, self._volume - value)
        message = f"volume decreased -{value}%"
        self.__output_service.message(message)

