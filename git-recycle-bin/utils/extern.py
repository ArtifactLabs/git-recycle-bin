import sys
import os
import subprocess

from git_recycle_bin.printer import printer

def exec(command, env={}):
    printer.debug("Run:", command, file=sys.stderr)
    return subprocess.check_output(command, env=os.environ|env, text=True).strip()

def exec_nostderr(command, env={}):
    printer.debug("Run:", command, file=sys.stderr)
    return subprocess.check_output(command, env=os.environ|env, text=True, stderr=subprocess.DEVNULL).strip()
