import sys
import os
import subprocess

from git_recycle_bin.printer import printer

def exec(command, env={}, cwd=None):
    printer.debug("Run:", command, file=sys.stderr)
    return subprocess.check_output(command, env=os.environ|env, text=True, cwd=cwd).strip()

def exec_nostderr(command, env={}, cwd=None):
    printer.debug("Run:", command, file=sys.stderr)
    return subprocess.check_output(command, env=os.environ|env, text=True, cwd=cwd,
                                   stderr=subprocess.DEVNULL).strip()

def jq_unsafe(command, input, env=None):
    """
    Run jq command and return the output.
    """
    env = env or {}
    printer.debug("Run jq:", command, file=sys.stderr)
    return subprocess.check_output(['jq'] + command, input=input, env=os.environ|env, text=True).strip()

def jq(command, input, env=None):
    """
    Run jq command and return the output, ignoring errors.
    """
    env = env or {}
    try:
        return jq_unsafe(command, input, env)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        printer.error(f"jq command failed: {e}", file=sys.stderr)
        return None
