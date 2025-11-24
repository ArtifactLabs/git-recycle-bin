import sys
from colorama import Fore, Style

class Printer:

    def __init__(self, verbosity: int = 1, colorize: bool = True):
        self.verbosity = verbosity
        self.colorize = colorize

    def _print(self, color, *args, file=sys.stdout):
        message = " ".join(str(x) for x in args)
        print(self.strcolor(color, message), file=file)

    def always(self, *args, file=sys.stdout):
        self._print(Fore.BLUE, *args, file=file)

    def error(self, *args, file=sys.stdout):
        self._print(Fore.RED, *args, file=file)

    def high_level(self, *args, file=sys.stdout):
        if self.verbosity >= 1:
            self._print(Fore.GREEN, *args, file=file)

    def detail(self, *args, file=sys.stdout):
        if self.verbosity >= 2:
            self._print(Fore.BLUE, *args, file=file)

    def debug(self, *args, file=sys.stdout):
        if self.verbosity >= 3:
            self._print(Fore.YELLOW, *args, file=file)

    def strcolor(self, color, message):
        if self.colorize:
            return color + message + Style.RESET_ALL
        else:
            return message

printer = Printer(verbosity=2, colorize=True)
