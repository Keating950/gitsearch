import os
import subprocess
import curses
from typing import Union


def format_validate_path(path: str) -> Union[Exception, str]:
    abs_path = os.path.expanduser(path).strip()
    if not os.path.isdir(abs_path):
        raise FileNotFoundError
    return abs_path


def clone_repo(path: str, url: str) -> bool:
    og_cwd = os.getcwd()
    DEVNULL = open(os.devnull, 'w')
    try:
        os.chdir(path)
        subprocess.call(["git", "clone", url], stdout=DEVNULL)
    except Exception as e:
        curses.endwin()
        raise e
    os.chdir(og_cwd)
    return True
