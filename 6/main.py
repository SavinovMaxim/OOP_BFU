import inspect
import string
from collections import deque
from typing import Dict, Optional, Any

from commands.abstract import Command
from commands.media import MediaPlayerCommand
from commands.printable import PrintCharCommand
from commands.volume import VolumeUpCommand, VolumeDownCommand
from services.media.base import MediaPlayer
from services.output.base import ConsoleAndFileOutput
from services.volume.base import VolumeService
from states.loader import KeyboardStateLoader
from states.memento import KeyboardMemento
from states.saver import KeyboardStateSaver


class Keyboard:
    def __init__(self):
        self.output_service = ConsoleAndFileOutput()
        self.volume_service = VolumeService(self.output_service)
        self.media_player = MediaPlayer(self.output_service)

        self.key_bindings: Dict[str, Command] = {}

        # История команд для undo/redo
        self.command_history: deque[Command] = deque()
        self.redo_stack: deque[Command] = deque()

        self.state_loader = KeyboardStateLoader()
        self.state_saver = KeyboardStateSaver()

        # Инициализация стандартных команд
        self._init_default_bindings()

        # Загрузка сохраненных привязок
        self._load_bindings()

    def _init_default_bindings(self) -> None:
        # стандартные букв
        for char in string.ascii_lowercase:
            self.add_binding(char, PrintCharCommand(char, self.output_service))

        # стандартн цифр
        for char in string.digits:
            self.add_binding(char, PrintCharCommand(char, self.output_service))

        # специальные команды
        self.add_binding("ctrl++", VolumeUpCommand(self.volume_service))
        self.add_binding("ctrl+-", VolumeDownCommand(self.volume_service))
        self.add_binding("ctrl+p", MediaPlayerCommand(self.media_player))

    def create_memento(self) -> KeyboardMemento:
        serializable_bindings = {}

        for key, command in self.key_bindings.items():
            command_type = type(command).__name__
            serializable_bindings[key] = {'command_type': command_type}

            # доп параметры
            serializable_bindings[key].update(command.save_data)

        return KeyboardMemento(serializable_bindings)

    def restore_from_memento(self, memento: Optional[Dict[str, Dict[str, Any]]]) -> None:
        def _initialize(_cls, *args, **kwargs):
            kwargs.update(self.__dict__)
            sig = inspect.signature(_cls.__init__)
            valid_params = sig.parameters.keys()
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_params}

            return _cls(*args, **filtered_kwargs)

        for key, binding_info in memento.items():
            data = binding_info.copy()
            command_type = data.pop('command_type', '')
            cls: object = globals()[command_type]
            obj = _initialize(cls, **data)
            self.add_binding(key, obj)

    def _load_bindings(self) -> None:
        loaded_state = self.state_loader.load()
        if loaded_state:
            self.restore_from_memento(loaded_state)

    def add_binding(self, key: str, command: Command) -> None:
        self.key_bindings[key] = command
        self.state_saver.save(self.create_memento())

    def press_key(self, key: str) -> None:
        spec_keys = {
            "undo": self.undo,
            "redo": self.redo,
        }
        if spec_key := spec_keys.get(key):
            spec_key()
            return

        if key in self.key_bindings:
            command = self.key_bindings[key]
            command.execute()
            self.command_history.append(command)
            # Очищаем стек redo после выполнения новой команды
            self.redo_stack = []
        else:
            raise Exception()
            # print(f"Нет привязки для клавиши: {key}")

    def undo(self) -> None:
        if self.command_history:
            command = self.command_history.pop()
            command.undo()
            self.redo_stack.append(command)
            self.output_service.message("undo", need_write=False)

    def redo(self) -> None:
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute()
            self.command_history.append(command)
            self.output_service.message("redo", need_write=False)


def main():
    keyboard = Keyboard()

    print("Виртуальная клавиатура готова к использованию.")
    print("Введите символы или команды (undo, redo):")

    while True:
        key = input().strip()
        if key == "exit":
            break
        keyboard.press_key(key)


if __name__ == "__main__":
    main()