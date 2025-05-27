from abc import abstractmethod, ABC


class AbstractMediaPlayer(ABC):

    @property
    @abstractmethod
    def is_playing(self) -> bool:
        """Проверка запущен ли медиа плеер"""
        ...

    @abstractmethod
    def play(self):
        """Запуск плеера"""
        ...

    @abstractmethod
    def stop(self):
        """Остановка плеера"""
        ...
