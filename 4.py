from typing import Protocol, Any


# 1. Интерфейс слушателя изменений
class PropertyChangedListenerProtocol(Protocol):
    def on_property_changed(self, obj: Any, property_name: str) -> None:
        ...


# 2. Интерфейс объекта, уведомляющего об изменениях
class DataChangedProtocol(Protocol):
    def add_property_changed_listener(self, listener: PropertyChangedListenerProtocol) -> None: ...
    def remove_property_changed_listener(self, listener: PropertyChangedListenerProtocol) -> None: ...


# 4. Интерфейс слушателя для валидации изменений
class PropertyChangingListenerProtocol(Protocol):
    def on_property_changing(self, obj: Any, property_name: str, old_value: Any, new_value: Any) -> bool:
        ...


# 5. Интерфейс объекта, уведомляющего перед изменением
class DataChangingProtocol(Protocol):
    def add_property_changing_listener(self, listener: PropertyChangingListenerProtocol) -> None: ...
    def remove_property_changing_listener(self, listener: PropertyChangingListenerProtocol) -> None: ...


# Класс с поддержкой обоих протоколов и свойствами
class ObservableValidatedClass(DataChangedProtocol, DataChangingProtocol):
    def __init__(self, name: str, age: int):
        self._name = name
        self._age = age
        self._changed_listeners: set[PropertyChangedListenerProtocol] = set()
        self._changing_listeners: set[PropertyChangingListenerProtocol] = set()

    def add_property_changed_listener(self, listener: PropertyChangedListenerProtocol) -> None:
        self._changed_listeners.add(listener)

    def remove_property_changed_listener(self, listener: PropertyChangedListenerProtocol) -> None:
        self._changed_listeners.remove(listener)

    def add_property_changing_listener(self, listener: PropertyChangingListenerProtocol) -> None:
        self._changing_listeners.add(listener)

    def remove_property_changing_listener(self, listener: PropertyChangingListenerProtocol) -> None:
        self._changing_listeners.remove(listener)

    def _notify_property_changing(self, property_name, old_value, new_value) -> bool:
        for listener in self._changing_listeners:
            if not listener.on_property_changing(self, property_name, old_value, new_value):
                return False
        return True

    def _notify_property_changed(self, property_name):
        for listener in self._changed_listeners:
            listener.on_property_changed(self, property_name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value != self._name and self._notify_property_changing("name", self._name, value):
            self._name = value
            self._notify_property_changed("name")

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        if value != self._age and self._notify_property_changing("age", self._age, value):
            self._age = value
            self._notify_property_changed("age")


class PrintChangeListener:
    def on_property_changed(self, obj, property_name):
        print(f"[Изменено] {property_name} -> {getattr(obj, property_name)}")


class AgeValidator:
    def on_property_changing(self, obj, property_name, old_value, new_value) -> bool:
        if property_name == "age" and (new_value < 0 or new_value > 150):
            print(f"[Невалидно] Неверный возраст: {new_value}")
            return False
        return True


class NameValidator:
    def on_property_changing(self, obj, property_name, old_value, new_value) -> bool:
        if property_name == "name" and not new_value.strip():
            print("[Невалидно] Имя не может быть пустым.")
            return False
        return True


# Демонстрация работы
if __name__ == "__main__":
    person = ObservableValidatedClass("Иван", 30)

    person.add_property_changed_listener(PrintChangeListener())
    person.add_property_changing_listener(AgeValidator())
    person.add_property_changing_listener(NameValidator())

    person.name = "Алексей"        # Проходит валидацию
    person.name = ""               # Невалидно
    person.age = 200               # Невалидно
    person.age = 35               # Проходит валидацию
