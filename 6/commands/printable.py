from commands.abstract import Command
from services.output.abstract import AbstractOutputService


class PrintCharCommand(Command):
    def __init__(self, char: str, output_service: AbstractOutputService):
        self._char = char
        self._output_service = output_service

    @property
    def save_data(self) -> dict:
        return {"char": self._char}

    @property
    def char(self):
        return self._char

    def execute(self) -> None:
        self._output_service.char(self._char)

    def undo(self) -> None:
        self._output_service.remove_last_char()
