#!/usr/bin/env python3

from MainWindow import MainWindow
import FetchResults
import argparse
import curses
import RepoCloner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", metavar="query string", type=str, nargs=1,
                        help="A quoted query string")
    parser.add_argument("--sort", metavar="sort by", type=str, nargs=1,
                        help="sort by stars, forks, help-wanted-issues, "
                             "or updated."
                             "Default is best match.")
    parser.add_argument("--order", metavar="order", type=str, nargs=1,
                        help="asc or desc. Default is descending")
    parser.add_argument("--lang", metavar="lang", type=str, nargs=1,
                        help="Restrict results by language.")
    arg_namespace = parser.parse_args()
    # splitting multi-word double-quoted query arguments
    arg_namespace.query = str(arg_namespace.query[0]).split()
    return arg_namespace


if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    formatted_args = parse_args()
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
                path_f = RepoCloner.format_validate_path(path)
            except FileNotFoundError:
                main_window.draw_path_error_window(path)
                continue
            RepoCloner.clone_repo(path_f, url)
            main_window.clear_popup_win()
    except KeyboardInterrupt:
        pass
    finally:
        curses.endwin()
