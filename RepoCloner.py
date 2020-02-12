import os
import subprocess
import curses
from typing import Tuple


def format_validate_path(path: str) -> Tuple[str, bool]:
    abs_path = os.path.expanduser(path).strip()
    return abs_path, os.path.isdir(abs_path)


def clone_repo(path: bytes, url: bytes) -> bool:
    clone_url = url.decode("utf-8")
    og_cwd = os.getcwd()
    FNULL = open(os.devnull, 'w')
    try:
        os.chdir(path)
        subprocess.call(["git", "clone", clone_url], stdout=FNULL)
    except Exception as e:
        curses.endwin()
        raise e
    os.chdir(og_cwd)
    return True
