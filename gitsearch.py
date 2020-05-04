#!/usr/bin/env python3

import argparse
import curses
import json
import re
from os import chdir, getcwd
from subprocess import check_call, DEVNULL, CalledProcessError
from typing import Union, Tuple, List

import certifi
import urllib3

from MainWindow import MainWindow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="""A simple command line utility for\
                             searching for and cloning repos from Github.
                             Move the cursor and turn pages with\
                             Vim-style hjkl inputs."""
    )
    parser.add_argument(
        "query",
        metavar='"query"',
        type=str,
        nargs=1,
        help="A quoted query string.",
    )
    parser.add_argument(
        "--sort",
        metavar="statistic",
        type=str,
        nargs=1,
        choices=("stars", "forks", "help-wanted-issues", "updated"),
        help="Sort by stars, forks, help-wanted-issues, or updated."
             " Default is best match.",
    )
    parser.add_argument(
        "--order",
        metavar="asc, desc",
        type=str,
        nargs=1,
        choices=("asc", "desc"),
        help="asc or desc. Default is descending.",
    )
    parser.add_argument(
        "--lang",
        metavar="lang",
        type=str,
        nargs=1,
        help="Restrict results by programming language.",
    )
    arg_namespace = parser.parse_args()
    # splitting multi-word double-quoted query arguments for proper url formatting
    arg_namespace.query = str(arg_namespace.query[0]).split()
    return arg_namespace


def format_validate_path(dest_path: str) -> Union[Exception, str]:
    abs_path = os.path.expanduser(dest_path).strip()
    if not os.path.isdir(abs_path):
        raise FileNotFoundError
    return abs_path


def is_url(text: str) -> bool:
    return bool(re.match(
        r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.["
        r"a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&/=]*)",
        text,
    ))


def format_query(args: argparse.Namespace) -> str:
    arg_dict = dict(vars(args))
    url = "https://api.github.com/search/repositories"
    # GitHub API expects multi-word queries to be joined together with the + symbol
    qlist = arg_dict.pop("query")
    qstring = qlist.pop(0)
    for word in qlist:
        qstring += f"+{word}"
    # it also expects language to be part of the query string, so merging those
    # attributes here
    if arg_dict["lang"] is not None:
        # subscripting because a list is returned, even though its always one item long
        lang_str = arg_dict.pop("lang")[0].replace(" ", "+")
        qstring += f"+language:{lang_str}"
    url += f"?q={qstring}"
    # Finally, deal with any other arguments
    for k, v in arg_dict.items():
        if v is not None:
            url += f"&{k}={v}"
    return url


def search(args: argparse.Namespace) -> List[dict]:
    search_url = format_query(args)
    http = urllib3.PoolManager(
        headers={"User-Agent": "Keating950/gitsearch"},
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where()
    )
    resp = http.request("GET", search_url)
    return json.loads(resp.data.decode("utf-8"))["items"]


def clone_repo(clone_dest: str, repo_url: str) -> None:
    orig_wd = getcwd()
    chdir(clone_dest)
    try:
        check_call(["git", "clone", repo_url], stdout=DEVNULL, stderr=DEVNULL)
    except CalledProcessError as cpe:
        chdir(orig_wd)
        raise cpe
    chdir(orig_wd)


def input_stream(window: MainWindow) -> Tuple[str, str]:
    curses.curs_set(0)
    window.chgat(0, 0, curses.A_STANDOUT)
    while True:
        y, _ = window.getyx()
        c = window.getkey()
        if c == "j":
            window.move(y + 1)
        elif c == "k":
            if y - 1 >= 0:
                window.move(y - 1)
        elif c == "l":
            window.turn_page(1)
            window.move(y)
        elif c == "h":
            if window.turn_page(-1):
                window.move(y)
        elif c == "\n":
            repo_url = window.instr(y, 0).strip().decode("utf-8")
            if is_url(repo_url):
                dest_path = window.path_prompt()
                window.touchwin()
                return dest_path, repo_url
        elif c == "q":
            raise KeyboardInterrupt()

        window.refresh()


if __name__ == "__main__":
    formatted_args = parse_args()
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    try:
        entries = search(formatted_args)
    except Exception as e:
        curses.endwin()
        raise e
    main_window = MainWindow(stdscr, entries)
    try:
        while True:
            path, url = input_stream(main_window)
            if not path:
                continue
            try:
                path_f = format_validate_path(path)
                clone_repo(path_f, url)
                main_window.draw_clone_success_msg(url.split("/")[-1], path_f)
            except FileNotFoundError:
                main_window.draw_path_error_window(path)
                continue
            except Exception as e:
                curses.endwin()
                raise e
    except KeyboardInterrupt:
        pass
    finally:
        curses.endwin()
