import os
import subprocess
import sys
from typing import Mapping, Sequence

from printer import printer

def exec(command: Sequence[str], env: Mapping[str, str] | None = None) -> str:
    """Execute a command and return its output."""
    printer.debug("Run:", command, file=sys.stderr)
    env_combined = os.environ | (env or {})
    return subprocess.check_output(command, env=env_combined, text=True).strip()

def exec_nostderr(command: Sequence[str], env: Mapping[str, str] | None = None) -> str:
    """Execute a command discarding stderr and return its output."""
    printer.debug("Run:", command, file=sys.stderr)
    env_combined = os.environ | (env or {})
    return subprocess.check_output(
        command,
        env=env_combined,
        text=True,
        stderr=subprocess.DEVNULL,
    ).strip()
