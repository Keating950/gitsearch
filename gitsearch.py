from MainWindow import MainWindow
import FetchResults
from Entry import Entry
from EntryPages import EntryPages
import argparse
import sys
import curses
from curses import textpad
import re


def url_popup(url: bytes or str):
    if not re.match(
            r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.["
            r"a-zA-Z0-9("
            r")]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
            url.decode("utf-8")):
        return
    quarter_lines = curses.LINES // 4
    quarter_cols = curses.COLS // 4
    half_lines = curses.LINES // 2
    half_cols = curses.COLS // 2
    input_window = curses.newwin(half_lines, half_cols,
                                 quarter_lines, quarter_cols)
    textpad.rectangle(stdscr, quarter_lines - 1, quarter_cols - 1,
                      int(half_lines * 1.5) + 1,
                      int(half_cols * 1.5) + 1)
    # centering text by taking half_cols - (len_of_phrase/2)
    input_window.addstr(quarter_lines - 1, half_cols // 2 - 10,
                        "Enter path to clone:")
    input_window.addstr(quarter_lines + 2,
                        f"{' ' * (half_lines - 1)}", curses.A_UNDERLINE)
    curses.setsyx(quarter_lines + 2, half_lines + 1)
    stdscr.refresh()
    box = textpad.Textbox(input_window)
    box.edit()
    return box.gather()


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
    main_window = MainWindow(stdscr)
    main_window.main(parse_args())
