#!/usr/bin/env python3

import argparse
import curses
import os
from typing import Union, Tuple

import FetchResults
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


def input_stream(window: MainWindow) -> Tuple[str, str]:
    curses.curs_set(0)
    window.chgat(0, 0, curses.A_STANDOUT)
    while True:
        y, _ = window.getyx()
        c = window.getkey()
        if c == "j":
            if y + 1 < curses.LINES:
                window.move(y + 1, 0)
        elif c == "k":
            if y - 1 >= 0:
                window.move(y - 1, 0)
        elif c == "l":
            window.turn_page(1)
            window.move(y, 0)
        elif c == "h":
            if window.turn_page(-1):
                window.move(y, 0)
        elif c == "\n":
            repo_url = window.instr(y, 0).strip().decode("utf-8")
            if FetchResults.is_url(repo_url):
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
        entries = FetchResults.search(formatted_args)
    except Exception as e:
        curses.endwin()
        raise e
    main_window = MainWindow(stdscr, entries)
    try:
        while True:
            path, url = input_stream(main_window)
            try:
                path_f = format_validate_path(path)
                FetchResults.clone_repo(path_f, url)
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
