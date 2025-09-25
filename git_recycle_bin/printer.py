"""Printing utilities with color support and verbosity levels."""
import sys
from typing import Any, Protocol, TextIO
from colorama import Fore, Style

class Stringable(Protocol):
    """Protocol for objects that can be converted to strings."""
    def __str__(self) -> str: ...

class Printer:
    """Printer class with color support and verbosity level control."""

    def __init__(self, verbosity: int = 1, colorize: bool = True):
        """Initialize printer with verbosity and color settings.
        
        :param verbosity: Verbosity level (0=silent, 1=normal, 2=detailed, 3=debug)
        :param colorize: Whether to use colored output
        """
        self.verbosity = verbosity
        self.colorize = colorize

    def _print(self, color: Stringable, *args: Any, file: TextIO = sys.stdout) -> None:
        """Internal print method with color support."""
        message = " ".join(str(x) for x in args)
        print(self.strcolor(color, message), file=file)

    def always(self, *args: Any, file: TextIO = sys.stdout) -> None:
        """Print message always, regardless of verbosity level."""
        self._print(Fore.BLUE, *args, file=file)

    def error(self, *args: Any, file: TextIO = sys.stdout) -> None:
        """Print error message in red color."""
        self._print(Fore.RED, *args, file=file)

    def high_level(self, *args: Any, file: TextIO = sys.stdout) -> None:
        """Print high-level message if verbosity >= 1."""
        if self.verbosity >= 1:
            self._print(Fore.GREEN, *args, file=file)

    def detail(self, *args: Any, file: TextIO = sys.stdout) -> None:
        """Print detailed message if verbosity >= 2."""
        if self.verbosity >= 2:
            self._print(Fore.BLUE, *args, file=file)

    def debug(self, *args: Any, file: TextIO = sys.stdout) -> None:
        """Print debug message if verbosity >= 3."""
        if self.verbosity >= 3:
            self._print(Fore.YELLOW, *args, file=file)

    def strcolor(self, color: Stringable, message: str) -> str:
        """Apply color to message if colorization is enabled.
        
        :param color: Color object to apply
        :param message: Message to colorize
        :returns: Colorized message or plain message
        """
        if self.colorize:
            return str(color) + message + str(Style.RESET_ALL)
        return message

printer = Printer(verbosity=2, colorize=True)
