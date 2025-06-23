from __future__ import annotations
from typing import Self, Optional
import json
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        ...

    @abstractmethod
    def undo(self) -> None:
        ...

    @abstractmethod
    def redo(self) -> None:
        ...


class PrintCharCommand(Command):
    text = ""  # Хранение всего текста

    def __init__(self, char: str) -> None:
        self.char = char

    def execute(self) -> str:
        PrintCharCommand.text += self.char
        return PrintCharCommand.text

    def undo(self) -> str:
        PrintCharCommand.text = PrintCharCommand.text[:-1]
        return PrintCharCommand.text

    def redo(self) -> str:
        return self.execute()


class VolumeUpCommand(Command):
    def __init__(self, amount: int = 20, current_volume: int = 50) -> None:
        self.amount = amount
        self.current_volume = current_volume

    def execute(self) -> str:
        self.current_volume += self.amount
        return f"volume increased +{self.amount}% (now: {self.current_volume}%)"

    def undo(self) -> str:
        self.current_volume -= self.amount
        return f"volume decreased +{self.amount}% (now: {self.current_volume}%)"

    def redo(self) -> str:
        return self.execute()


class VolumeDownCommand(Command):
    def __init__(self, amount: int = 20, current_volume: int = 50) -> None:
        self.amount = amount
        self.current_volume = current_volume

    def execute(self) -> str:
        self.current_volume -= self.amount
        return f"volume decreased -{self.amount}% (now: {self.current_volume}%)"

    def undo(self) -> str:
        self.current_volume += self.amount
        return f"volume increased -{self.amount}% (now: {self.current_volume}%)"

    def redo(self) -> str:
        return self.execute()


class MediaPlayerCommand(Command):
    def __init__(self, is_playing: bool = False) -> None:
        self.is_playing = is_playing

    def execute(self) -> str:
        self.is_playing = True
        return "media player launched"

    def undo(self) -> str:
        self.is_playing = False
        return "media player closed"

    def redo(self) -> str:
        return self.execute()


class KeyboardMemento:
    def __init__(self, state: dict) -> None:
        self.state = state

    @classmethod
    def from_keyboard(cls, keyboard) -> Self:
        text = PrintCharCommand.text

        key_bindings = {}
        for key, command in keyboard.key_bindings.items():
            if command is None:
                key_bindings[key] = None
            else:
                key_bindings[key] = {
                    'class': str(command.__class__.__name__),
                    'state': command.__dict__.copy()
                }

        return cls({
            'text': text,
            'key_bindings': key_bindings,
            'history': [command["key"] for command in keyboard.history],
            'undo_stack': [command["key"] for command in keyboard.undo_stack]
        })


class VirtualKeyboard:
    def __init__(self) -> None:
        self.key_bindings: dict[str, Command] = {}
        self.history: list[dict[str, Command]] = []
        self.undo_stack: list[dict[str, Command]] = []

        self.init_default_bindings()

    def init_default_bindings(self) -> None:
        self.bind_key("a", PrintCharCommand("a"))
        self.bind_key("b", PrintCharCommand("b"))
        self.bind_key("c", PrintCharCommand("c"))
        self.bind_key("d", PrintCharCommand("d"))
        self.bind_key("ctrl++", VolumeUpCommand())
        self.bind_key("ctrl+-", VolumeDownCommand())
        self.bind_key("ctrl+p", MediaPlayerCommand())
        self.bind_key("undo", None)
        self.bind_key("redo", None)

    def bind_key(self, key: str, command: Optional[Command]) -> None:
        self.key_bindings[key] = command

    def press_key(self, key: str) -> str | None:
        if key == "undo":
            return self.undo()
        elif key == "redo":
            return self.redo()

        command = self.key_bindings.get(key)
        if not command and len(key) == 1:
            self.bind_key(key, PrintCharCommand(key))
            command = self.key_bindings.get(key)
        if command:
            result = command.execute()
            self.history.append({"key": key, "command": command})
            self.undo_stack.clear()
            return result
        return f"Unknown key: {key}"

    def undo(self) -> str:
        if not self.history:
            return "Nothing to undo"

        command = self.history.pop()
        result = command["command"].undo()
        self.undo_stack.append(command)
        return f"undo: {result}"

    def redo(self) -> str:
        if not self.undo_stack:
            return "Nothing to redo"

        command = self.undo_stack.pop()
        result = command["command"].redo()
        self.history.append(command)
        return f"redo: {result}"

    def save_state(self, filename: str = "keyboard_state.json") -> None:
        memento = KeyboardMemento.from_keyboard(self)
        try:
            with open(filename, "w") as f:
                json.dump(memento.state, f, indent=4)
        except Exception as e:
            print(f"Error saving state: {e}")
            raise e

    def load_state(self, filename: str = "Labs/Lab6/data/keyboard_state.json") -> bool:
        try:
            with open(filename, "r") as f:
                state = json.load(f)

            PrintCharCommand.text = state['text']
            class_names = {cls.__name__: cls for cls in Command.__subclasses__()}

            self.key_bindings.clear()
            for key, command_data in state.get('key_bindings', {}).items():
                if command_data is None:
                    self.key_bindings[key] = None
                else:
                    command = class_names[command_data['class']](**command_data['state'])
                    self.key_bindings[key] = command

            self.history = [
                {"key": key, "command": self.key_bindings[key]}
                for key in state.get('history', [])
                if key in self.key_bindings.keys() and self.key_bindings[key] is not None
            ]

            self.undo_stack = [
                {"key": key, "command": self.key_bindings[key]}
                for key in state.get('undo_stack', [])
                if key in self.key_bindings.keys() and self.key_bindings[key] is not None
            ]
            return True
        except (FileNotFoundError, json.JSONDecodeError, KeyError, AttributeError) as e:
            print(f"Error loading state: {e}")
            return False

COLORING = "\033[{}m{}\033[0m"



if __name__ == "__main__":
    keyboard = VirtualKeyboard()

    if not keyboard.load_state():
        print(COLORING.format(33, "No saved state found, using defaults"))
    else:
        print(COLORING.format(33, "Keyboard state loaded"))
        print(COLORING.format(33, PrintCharCommand.text))

    with open("keyboard_log.txt", "w") as log_file:
        def print_and_log(message) -> None:
            print(COLORING.format(32, message))
            log_file.write(message + "\n")


        print_and_log(keyboard.press_key("a"))
        print_and_log(keyboard.press_key("b"))
        print_and_log(keyboard.press_key("c"))
        print_and_log(keyboard.press_key("undo"))
        print_and_log(keyboard.press_key("undo"))
        print_and_log(keyboard.press_key("redo"))
        print_and_log(keyboard.press_key("ctrl++"))
        print_and_log(keyboard.press_key("ctrl+-"))
        print_and_log(keyboard.press_key("ctrl+p"))
        print_and_log(keyboard.press_key("d"))
        print_and_log(keyboard.press_key("undo"))
        print_and_log(keyboard.press_key("undo"))

        keyboard.save_state()
        print_and_log("Keyboard state saved")