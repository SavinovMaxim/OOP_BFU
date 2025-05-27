import json
import os
from typing import Optional, Any

from config import settings
from services.serializer import JSONSerializer, AbstractSerializer


class KeyboardStateLoader:
    LOAD_MODE = 'r'

    def __init__(
            self,
            file_path: str = settings.DEFAULT_MEMENTO_FILE,
            serializer: AbstractSerializer = None
    ):
        self._file_path = file_path
        self.__serializer = serializer or JSONSerializer()

    def load(self) -> Optional[dict[str, dict[str, Any]]]:
        if not os.path.exists(self._file_path):
            return None

        try:
            with open(self._file_path, self.LOAD_MODE, encoding=settings.ENCODING) as f:
                return self.__serializer.load_file(f)
        except (json.JSONDecodeError, IOError):
            return None
