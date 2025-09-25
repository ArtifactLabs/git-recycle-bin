"""Utility functions for command execution and environment management."""
import sys
import os
import subprocess

from git_recycle_bin.printer import printer

def exec(command, env=None):  # pylint: disable=redefined-builtin
    """Execute command with merged environment and return stripped output.
    
    :param command: List of command and arguments to execute
    :param env: Additional environment variables to merge
    :returns: Stripped stdout from command execution
    """
    if env is None:
        env = {}
    printer.debug("Run:", command, file=sys.stderr)
    merged_env = dict(os.environ)
    merged_env.update(env)
    return subprocess.check_output(command, env=merged_env, text=True).strip()

def exec_nostderr(command, env=None):
    """Execute command with merged environment, suppressing stderr.
    
    :param command: List of command and arguments to execute
    :param env: Additional environment variables to merge
    :returns: Stripped stdout from command execution
    """
    if env is None:
        env = {}
    printer.debug("Run:", command, file=sys.stderr)
    merged_env = dict(os.environ)
    merged_env.update(env)
    return subprocess.check_output(
        command, env=merged_env, text=True, stderr=subprocess.DEVNULL
    ).strip()
