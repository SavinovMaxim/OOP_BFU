from typing import Protocol, List
import re
import sys
import socket
from datetime import datetime


class LogFilterProtocol(Protocol):
    def match(self, text: str) -> bool:
        pass


class SimpleLogFilter(LogFilterProtocol):
    def __init__(self, pattern: str):
        self.pattern = pattern

    def match(self, text: str) -> bool:
        try:
            return self.pattern in text
        except Exception as e:
            sys.stderr.write(f"SimpleLogFilter error: {e}\n")
            return False


class ReLogFilter(LogFilterProtocol):
    def __init__(self, pattern: str):
        try:
            self.regex = re.compile(pattern)
        except re.error as e:
            sys.stderr.write(f"Invalid regex pattern: {e}\n")
            raise

    def match(self, text: str) -> bool:
        try:
            return bool(self.regex.search(text))
        except Exception as e:
            sys.stderr.write(f"ReLogFilter error: {e}\n")
            return False


class LevelFilter(LogFilterProtocol):
    def __init__(self, level: str):
        try:
            self.level = level.upper()
        except AttributeError as e:
            sys.stderr.write(f"Invalid level type: {e}\n")
            raise

    def match(self, text: str) -> bool:
        try:
            return text.startswith(self.level)
        except Exception as e:
            sys.stderr.write(f"LevelFilter error: {e}\n")
            return False


class LogHandlerProtocol(Protocol):
    def handle(self, text: str):
        pass


class FileHandler(LogHandlerProtocol):
    def __init__(self, filename: str):
        try:
            self.filename = str(filename)
            # Проверяем возможность записи при инициализации
            with open(self.filename, "a", encoding='utf-8') as f:
                pass
        except (IOError, PermissionError, TypeError) as e:
            sys.stderr.write(f"FileHandler init error: {e}\n")
            raise

    def _handle(self, text: str):
        try:
            with open(self.filename, "a", encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {text}\n")
        except UnicodeEncodeError:
            # Попробуем записать без специальных символов
            with open(self.filename, "a", encoding='ascii', errors='replace') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {text.encode('ascii', errors='replace').decode('ascii')}\n")

    def handle(self, text: str):
        try:
            self._handle(text)
        except (IOError, PermissionError) as e:
            sys.stderr.write(f"FileHandler error: {e}\n")
        except Exception as e:
            sys.stderr.write(f"Unexpected FileHandler error: {e}\n")


class SocketHandler(LogHandlerProtocol):
    def __init__(self, host: str, port: int):
        try:
            self.host = str(host)
            self.port = int(port)
            if not 0 < self.port < 65536:
                raise ValueError("Port must be between 1 and 65535")
        except (ValueError, TypeError) as e:
            sys.stderr.write(f"SocketHandler init error: {e}\n")
            raise

    def handle(self, text: str):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                try:
                    s.connect((self.host, self.port))
                    s.sendall(f"{text}\n".encode('utf-8'))
                except (socket.timeout, ConnectionRefusedError) as e:
                    sys.stderr.write(f"Socket connection error: {e}\n")
                except socket.error as e:
                    sys.stderr.write(f"Socket communication error: {e}\n")
        except Exception as e:
            sys.stderr.write(f"Unexpected SocketHandler error: {e}\n")


class ConsoleHandler(LogHandlerProtocol):
    def __init__(self, use_stderr: bool = False):
        self.use_stderr = bool(use_stderr)

    def handle(self, text: str):
        try:
            if self.use_stderr:
                sys.stderr.write(f"{text}\n")
            else:
                print(text)
        except Exception as e:
            sys.stderr.write(f"ConsoleHandler error: {e}\n")


class SyslogHandler(LogHandlerProtocol):
    def handle(self, text: str):
        try:
            sys.stderr.write(f"SYSLOG: {text}\n")
        except Exception as e:
            sys.stderr.write(f"SyslogHandler error: {e}\n")


class Logger:
    def __init__(self, _filters: List[LogFilterProtocol], _handlers: List[LogHandlerProtocol]):
        try:
            self.__filters = list(_filters) if _filters else []
            self.__handlers = list(_handlers) if _handlers else []
        except Exception as e:
            sys.stderr.write(f"Logger init error: {e}\n")
            raise

    def log(self, text: str):
        try:
            if not isinstance(text, str):
                raise TypeError("Log message must be a string")
                
            if all(f.match(text) for f in self.__filters):
                for handler in self.__handlers:
                    try:
                        handler.handle(text)
                    except Exception as e:
                        sys.stderr.write(f"Handler error: {e}\n")
        except Exception as e:
            sys.stderr.write(f"Logging error: {e}\n")


# Демонстрация работы
if __name__ == "__main__":
    print("Демонстрация работы системы логирования")
    
    try:
        # Создаем различные фильтры
        error_filter = SimpleLogFilter("ERROR")
        warning_filter = SimpleLogFilter("WARNING")
        digit_filter = ReLogFilter(r"\d+")
        level_filter = LevelFilter("INFO")
        
        # Создаем обработчики
        console_handler = ConsoleHandler()
        error_file_handler = FileHandler("error_logs.txt")
        all_file_handler = FileHandler("all_logs.txt")
        syslog_handler = SyslogHandler()
        
        # Пример 1: Логировать только ERROR сообщения с цифрами в консоль и файл
        print("\nПример 1: ERROR логи с цифрами")
        logger1 = Logger(
            [error_filter, digit_filter],
            [console_handler, error_file_handler]
        )
        
        logger1.log("ERROR: Ошибка 404")
        logger1.log("WARNING: Произошло что-то необычное")
        logger1.log("ERROR: Ещё ошибка")
        logger1.log(123)  # Проверка обработки нестрокового сообщения
        
        # Пример 2: Логировать все INFO сообщения в файл и syslog
        print("\nПример 2: INFO логи")
        logger2 = Logger(
            [level_filter],
            [all_file_handler, syslog_handler]
        )
        
        logger2.log("INFO: Система запущена")
        logger2.log("INFO: Пользователь вошел в систему")
        logger2.log("WARNING: Мало места на диске")
        
        # Пример 3: Логировать все сообщения в консоль
        print("\nПример 3: Все логи")
        logger3 = Logger(
            [],  
            [console_handler]
        )
        
        logger3.log("DEBUG: Подробная информация")
        logger3.log("INFO: Просто для вашей информации")
        logger3.log("ERROR: Ошибка!")
        
    except Exception as e:
        sys.stderr.write(f"Demo error: {e}\n")
        sys.exit(1)