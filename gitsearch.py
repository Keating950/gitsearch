#!/usr/bin/env python3

import argparse
import curses
import os
from typing import Union
import FetchResults
from MainWindow import MainWindow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="A command line program to search for"
                                                 "and clone repos from GitHub.")
    parser.add_argument("--query", metavar="query string", type=str, nargs=1,
                        help="A quoted query string", required=True)
    parser.add_argument("--sort", metavar="sort by", type=str, nargs=1,
                        help="sort by stars, forks, help-wanted-issues, "
                             "or updated."
                             "Default is best match.")
    parser.add_argument("--order", metavar="order", type=str, nargs=1,
                        help="asc or desc. Default is descending")
    parser.add_argument("--lang", metavar="lang", type=str, nargs=1,
                        help="Restrict results by language.")
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
