#!/usr/bin/env python3

import argparse
import curses
import os
from typing import Union
import FetchResults
from MainWindow import MainWindow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=
                                     """A simple command line utility for\
                                         searching for and cloning repos from\
                                         Github.\nMove the cursor with Vim-style hjkl\
                                         inputs. Flip pages with Tab and Shift+Tab."""
                                     )
    parser.add_argument("query",
                        metavar="\"query\"",
                        type=str,
                        nargs=1,
                        help="A quoted query string.",
                        )
    parser.add_argument("--sort",
                        metavar="statistic",
                        type=str,
                        nargs=1,
                        choices=("stars", "forks", "help-wanted-issues", "updated"),
                        help="Sort by stars, forks, help-wanted-issues, or updated."
                             " Default is best match."
                        )
    parser.add_argument("--order",
                        metavar="asc, desc",
                        type=str,
                        nargs=1,
                        choices=("asc", "desc"),
                        help="asc or desc. Default is descending."
                        )
    parser.add_argument("--lang",
                        metavar="lang",
                        type=str,
                        nargs=1,
                        help="Restrict results by programming language."
                        )
    arg_namespace = parser.parse_args()
    # splitting multi-word double-quoted query arguments for proper url formatting
    arg_namespace.query = str(arg_namespace.query[0]).split()
    return arg_namespace


def format_validate_path(path: str) -> Union[Exception, str]:
    abs_path = os.path.expanduser(path).strip()
    if not os.path.isdir(abs_path):
        raise FileNotFoundError
    return abs_path


if __name__ == "__main__":
    formatted_args = parse_args()
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    entries = FetchResults.gen_entries(
        FetchResults.fetch(formatted_args)
    )
    main_window = MainWindow(stdscr,
                             formatted_args,
                             entries)

    try:
        while True:
            path, url = main_window.input_stream()
            try:
                path_f = format_validate_path(path)
            except FileNotFoundError:
                main_window.draw_path_error_window(path)
                continue
            FetchResults.clone_repo(path_f, url)
            main_window.clear_popup_win(url.split("/")[-1], path_f)
    except KeyboardInterrupt:
        pass
    finally:
        curses.endwin()
