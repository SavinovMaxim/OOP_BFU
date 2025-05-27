from config import settings
from .abstract import AbstractOutputService


class ConsoleAndFileOutput(AbstractOutputService):
    # Можно поменять w на другой мод, чтобы при запуске не удалять все
    WRITE_MODE = 'w'
    DEFAULT_FILE = 'keyboard_output.txt'

    def __init__(
            self,
            *,
            default_text: str = "",
            output_file: str = DEFAULT_FILE,
    ):
        self.__text = default_text
        self.__output_file = output_file

        self._file = open(output_file, self.WRITE_MODE, encoding=settings.ENCODING)

    def char(self, char: str) -> None:
        self.__text += char
        print(char)
        self._file.write(f"{self.__text}\n")
        self._file.flush()

    def message(self, message: str, need_write: bool = True) -> None:
        print(message)
        if need_write:
            self._file.write(f"{message}\n")
            self._file.flush()

    def remove_last_char(self) -> None:
        if not self.__text:
            return
        self.__text = self.__text[:-1]
        print("\b \b", end='')
        self._file.write(f"{self.__text}\n")
        self._file.flush()

    def __del__(self):
        self._file.close()
