import sys
from typing import Any, Protocol, TextIO
from colorama import Fore, Style

class Stringable(Protocol):
    def __str__(self) -> str: ...

class Printer:

    def __init__(self, verbosity: int = 1, colorize: bool = True):
        self.verbosity = verbosity
        self.colorize = colorize

    def _print(self, color: Stringable, *args: Any, file: TextIO = sys.stdout) -> None:
        message = " ".join(str(x) for x in args)
        print(self.strcolor(color, message), file=file)

    def always(self, *args: Any, file: TextIO = sys.stdout) -> None:
        self._print(Fore.BLUE, *args, file=file)

    def error(self, *args: Any, file: TextIO = sys.stdout) -> None:
        self._print(Fore.RED, *args, file=file)

    def high_level(self, *args: Any, file: TextIO = sys.stdout) -> None:
        if self.verbosity >= 1:
            self._print(Fore.GREEN, *args, file=file)

    def detail(self, *args: Any, file: TextIO = sys.stdout) -> None:
        if self.verbosity >= 2:
            self._print(Fore.BLUE, *args, file=file)

    def debug(self, *args: Any, file: TextIO = sys.stdout) -> None:
        if self.verbosity >= 3:
            self._print(Fore.YELLOW, *args, file=file)

    def strcolor(self, color: Stringable, message: str) -> str:
        if self.colorize:
            return str(color) + message + str(Style.RESET_ALL)
        else:
            return message

printer = Printer(verbosity=2, colorize=True)
