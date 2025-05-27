from typing import Any


class KeyboardMemento:
    def __init__(self, key_bindings: dict[str, dict[str, Any]]):
        self._state = key_bindings

    def get_state(self) -> dict[str, dict[str, Any]]:
        return self._state
