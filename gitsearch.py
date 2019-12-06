from entry import Entry
import ResultFetcher
import argparse
import sys
import curses
from curses import textpad
import re


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", metavar="query string", type=str, nargs=1,
                        help="A quoted query string")
    parser.add_argument("--sort", metavar="sort by", type=str, nargs=1,
                        help="sort by stars, forks, help-wanted-issues, or updated."
                             "Default is best match.")
    parser.add_argument("--order", metavar="order", type=str, nargs=1,
                        help="asc or desc. Default is descending")
    parser.add_argument("--lang", metavar="lang", type=str, nargs=1,
                        help="Restrict results by language.")
    arg_namespace = parser.parse_args()
    # splitting multi-word double-quoted query arguments
    arg_namespace.query = str(arg_namespace.query[0]).split()
    return arg_namespace


def gen_entry_objects(results: list) -> list:
    entries = []
    for repo in results:
        entry = Entry(repo['name'], repo['owner']['login'], int(repo['stargazers_count']),
                      repo['html_url'], repo.get('language'), repo.get('description'),
                      )
        entries.append(entry)
    return entries


def init_pad(contents):
    # each entry's length + space for a newline + 1 to account for zero-indexing
    sumlines = sum([entry.numlines for entry in contents]) + len(contents) + 1
    pad = curses.newpad(sumlines, curses.COLS)
    line_position = 0
    for entry in contents:
        entry.print_lines(pad, line_position)
        line_position += entry.numlines
        pad.addch(line_position, 0, "\n")
        line_position += 1
    return pad


def input_stream(pad, pad_max_y: int):
    pad_pos = 0
    stdscr.refresh()

    def mv_cursor_and_scroll(pad_pos, c):
        # scroll
        if c == curses.KEY_DOWN:
            return pad_pos + 1
        elif c == curses.KEY_UP:
            return pad_pos - 1

        # cursor movement and, if in first or last line, scroll
        y, x = curses.getsyx()
        if c == ord("j"):
            if y == curses.LINES - 1:
                return pad_pos + 1
            else:
                curses.setsyx(y + 1, x)
        elif c == ord("k"):
            if y == 0:
                if pad_pos > 0:
                    return pad_pos - 1
                else:
                    return pad_pos
            else:
                curses.setsyx(y - 1, x)
        elif c in {curses.KEY_LEFT, ord("h")}:
            if x - 1 < 0:
                return pad_pos
            else:
                curses.setsyx(y, x - 1)
        elif c in {curses.KEY_RIGHT, ord("l")}:
            if x + 1 > curses.COLS - 1:
                return pad_pos
            else:
                curses.setsyx(y, x + 1)

        return pad_pos

    def url_popup(url):
        if re.match(url,
                    "https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,"
                    "6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"):
            textpad.rectangle(stdscr, (uly := curses.LINES // 8),
                              (ulx := curses.COLS // 8),
                              uly * 2, ulx * 2)

        return

    while True:
        c = stdscr.getch()

        if c in {ord("h"), ord("j"), ord("k"), ord("l"),
                 curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT}:
            pad_pos = mv_cursor_and_scroll(pad_pos, c)
            if pad_pos < pad_max_y - curses.LINES:
                pad.refresh(pad_pos, 0, 0, 0, curses.LINES - 1, curses.COLS - 1)
            else:
                pad_pos = (pad_max_y - curses.LINES) - 1
            continue

        elif c == curses.KEY_ENTER:
            y, x = curses.getsyx()
            url = pad.instr(y, 0)
            url_popup(url)
            stdscr.refresh()


def main(stdscr):
    arg_str = ""
    for i in sys.argv:
        arg_str += str(i)

    formatted_args = parse_args()
    results = ResultFetcher.fetch_results(formatted_args)
    entry_list = gen_entry_objects(results)

    results_pad = init_pad(entry_list)
    results_pad.refresh(0, 0, 0, 0, curses.LINES - 1, curses.COLS - 1)
    pad_max_y = sum([entry.numlines for entry in entry_list]) + len(entry_list) + 1

    try:
        input_stream(results_pad, pad_max_y)
    except KeyboardInterrupt:
        pass
    finally:
        curses.endwin()


if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.wrapper(main)
