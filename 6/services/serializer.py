import json
from abc import ABC, abstractmethod
from typing import Any


class AbstractSerializer(ABC):
    @abstractmethod
    def load_file(self, data) -> Any:
        ...

    @abstractmethod
    def loads(self, data) -> Any:
        ...

    @abstractmethod
    def dump_file(self, f, data: Any) -> None:
        ...

    @abstractmethod
    def dumps(self, data) -> Any:
        ...


class JSONSerializer(AbstractSerializer):

    def load_file(self, data) -> Any:
        return json.load(data)

    def loads(self, data) -> Any:
        return json.loads(data)

    def dump_file(self, f, data: Any) -> None:
        return json.dump(data, f, indent=4)

    def dumps(self, data) -> Any:
        return json.dumps(data)
