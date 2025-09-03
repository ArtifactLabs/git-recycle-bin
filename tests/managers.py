import os
from contextlib import contextmanager

@contextmanager
def change_dir(path):
    original_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original_dir)

@contextmanager
def git_user_info():
    old_env = os.environ.copy()
    os.environ["GIT_AUTHOR_NAME"] = "mock"
    os.environ["GIT_AUTHOR_EMAIL"] = "mock@mock.mock"
    os.environ["GIT_COMMITTER_NAME"] = "mock"
    os.environ["GIT_COMMITTER_EMAIL"] = "mock@mock.mock"
    try:
        yield
    finally:
        os.environ = old_env
