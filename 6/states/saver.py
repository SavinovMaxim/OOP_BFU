from config import settings
from services.serializer import AbstractSerializer, JSONSerializer
from states.memento import KeyboardMemento


class KeyboardStateSaver:
    DUMP_MODE = "w"

    def __init__(
            self,
            file_path: str = settings.DEFAULT_MEMENTO_FILE,
            serializer: AbstractSerializer = None
    ):
        self.__file_path = file_path
        self.__serializer = serializer or JSONSerializer()

    def save(self, memento: KeyboardMemento) -> None:
        serializable_state = {}

        # Преобразуем состояние в сериализуемый формат
        for key, binding_info in memento.get_state().items():
            command_type = binding_info.pop('command_type', '')
            serializable_state[key] = {'command_type': command_type, **binding_info}

        with open(self.__file_path, self.DUMP_MODE, encoding=settings.ENCODING) as f:
            self.__serializer.dump_file(f, serializable_state)
