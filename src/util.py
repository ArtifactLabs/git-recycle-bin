import sys
import os
import subprocess
from printer import printer

def exec(command, env={}):
    printer.debug("Run:", command, file=sys.stderr)
    merged_env = dict(os.environ)
    merged_env.update(env)
    return subprocess.check_output(command, env=merged_env, text=True).strip()

def exec_nostderr(command, env={}):
    printer.debug("Run:", command, file=sys.stderr)
    merged_env = dict(os.environ)
    merged_env.update(env)
    return subprocess.check_output(command, env=merged_env, text=True, stderr=subprocess.DEVNULL).strip()
