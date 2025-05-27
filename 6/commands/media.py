from commands.abstract import Command
from services.media.abstract import AbstractMediaPlayer


class MediaPlayerCommand(Command):
    def __init__(self, media_player: AbstractMediaPlayer):
        self._media_player = media_player

    @property
    def save_data(self) -> dict:
        return {}

    def execute(self) -> None:
        self._media_player.play()

    def undo(self) -> None:
        self._media_player.stop()
