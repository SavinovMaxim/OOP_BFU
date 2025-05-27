import json
import os
from enum import Enum
from typing import Tuple, Dict, List


class Color(Enum):
    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    RESET = "\033[0m"


FONT_FILE = "font.json"

if os.path.exists(FONT_FILE):
    with open(FONT_FILE, "r", encoding="utf-8") as file:
        FONT_DATA = json.load(file)
else:
    raise FileNotFoundError(FONT_FILE)


class Printer:
    def __init__(self, color: Color, position: Tuple[int, int] | None = None, 
                 symbol: str = "*", font_size: int = 1):
        self.color = color
        self.symbol = symbol
        self.font_size = font_size
        self.original_position = (0, 0)
        self.position = position or self.original_position

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(Color.RESET.value, end="")

    @staticmethod
    def print(text: str, color: Color, position: Tuple[int, int] | None = None, 
              symbol: str = "*", font_size: int = 1):
        Printer._render_text(text, color, position, symbol, font_size)

    def print_text(self, text: str):
        Printer._render_text(text, self.color, self.position, self.symbol, self.font_size)

    @staticmethod
    def _scale_pattern(pattern: List[str], scale: int) -> List[str]:
        if scale == 1:
            return pattern
        
        scaled_pattern = []
        for line in pattern:
            scaled_line = ""
            for char in line:
                scaled_line += char * scale
            for _ in range(scale):
                scaled_pattern.append(scaled_line)
        return scaled_pattern

    @staticmethod
    def _render_text(text: str, color: Color, position: Tuple[int, int] | None, 
                    symbol: str, font_size: int):
        position = position or (0, 0)
        coordinate_settings = f"\033[{position[1]};{position[0]}H"
        print(color.value, end="")

        base_height = FONT_DATA['height']
        lines = ["" for _ in range(base_height * font_size)]
        
        for char in text.upper():
            if char in FONT_DATA["symbols"]:
                char_pattern = FONT_DATA["symbols"][char].split("\n")
                scaled_pattern = Printer._scale_pattern(char_pattern, font_size)
                
                for i, line in enumerate(scaled_pattern):
                    if symbol:
                        line = line.replace("*", symbol)
                    lines[i] += line + (" " * font_size * 2)

        for line in lines:
            print(coordinate_settings, line)
        print(Color.RESET.value, end="")


if __name__ == "__main__":
    # Статический вызов с разными размерами шрифта
    Printer.print("SMALL", Color.RED, (5, 5), "■", 1)
    Printer.print("MEDIUM", Color.GREEN, (5, 12), "●", 2)
    Printer.print("LARGE", Color.BLUE, (5, 25), "▲", 3)
    
    # Использование контекстного менеджера с разными размерами
    with Printer(Color.CYAN, (5, 40), "♥", 1) as small_printer:
        small_printer.print_text("LOVE")
    
    with Printer(Color.MAGENTA, (10, 40), "♦", 2) as medium_printer:
        medium_printer.print_text("LOVE")
    
    with Printer(Color.YELLOW, (20, 40), "♣", 3) as large_printer:
        large_printer.print_text("LOVE")
    