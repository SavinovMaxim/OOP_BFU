from commands.abstract import Command
from services.volume.abstract import AbstractVolumeService


# Команда для увеличения громкости
class VolumeUpCommand(Command):
    def __init__(self, volume_service: AbstractVolumeService, increment: int = 20):
        self._volume_service = volume_service
        self._increment = increment

    @property
    def save_data(self) -> dict:
        return {"increment": self._increment}

    def execute(self) -> None:
        self._volume_service.increase_volume(self._increment)

    def undo(self) -> None:
        self._volume_service.decrease_volume(self._increment)


# Команда для уменьшения громкости
class VolumeDownCommand(Command):
    def __init__(self, volume_service: AbstractVolumeService, decrement: int = 20):
        self._volume_service = volume_service
        self._decrement = decrement

    @property
    def save_data(self) -> dict:
        return {"decrement": self._decrement}

    def execute(self) -> None:
        self._volume_service.decrease_volume(self._decrement)

    def undo(self) -> None:
        self._volume_service.increase_volume(self._decrement)
