from io import StringIO
from printer import Printer


def test_printer_levels():
    buf = StringIO()
    p = Printer(verbosity=2, colorize=False)
    p.high_level('A', file=buf)
    p.detail('B', file=buf)
    p.debug('C', file=buf)
    lines = [line.strip() for line in buf.getvalue().splitlines()]
    assert lines == ['A', 'B']


def test_strcolor():
    p = Printer(colorize=True)
    colored = p.strcolor('\x1b[31m', 'msg')
    assert colored.startswith('\x1b[31m') and colored.endswith('\x1b[0m')
    p.colorize = False
    assert p.strcolor('x', 'msg') == 'msg'
