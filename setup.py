#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="git-recycle-bin",
    version="0.2.5",
    # Modules to import from other scripts:
    packages=find_packages(),
    install_requires=[
        "maya",
        "colorama",
        "dateparser",
    ],
    # Executables
    scripts=[
        "src/git_recycle_bin.py",
        "src/rbgit.py",
        "src/printer.py",
        "src/util_string.py",
        "src/util_file.py",
        "src/util_date.py",
        "src/util_sysinfo.py",
        "src/arg_parser.py",
        "src/list.py",
        "src/download.py",
        "src/commit_msg.py",
        "src/util.py",
    ],
)

