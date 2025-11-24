import os
from socket import gethostname
from getpass import getuser

def get_user() -> str:
    """ Return the current user's username """
    return os.environ.get('USER') or os.environ.get('USERNAME') or getuser()

def get_hostname() -> str:
    """ Return the system's hostname """
    return os.environ.get('HOSTNAME') or gethostname()
