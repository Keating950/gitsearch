from ResultFetcher import ResultFetcher
import sys
import curses
import os


def terminate_curses(stdscr):
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


def main(stdscr):
    arg_str = ""
    for i in sys.argv:
        arg_str += str(i)
    result_fetcher = ResultFetcher()
    results = result_fetcher.fetch_results()

    rows, cols = tuple(map(
        lambda x: int(x),
        os.popen('stty size', 'r').read().split()
    ))

    results_pad = curses.newpad(len(results) * 3, cols)

    sidebar = curses.newwin(rows, cols // 4, 0, 0)
    stdscr.refresh()
    sidebar.refresh()


if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.wrapper(main)
