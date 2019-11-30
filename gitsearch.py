import ResultFetcher
import sys
import curses
import os


def main(stdscr):
    arg_str = ""
    for i in sys.argv:
        arg_str += str(i)
    results = ResultFetcher.fetch_results()

    rows, cols = tuple(map(
        lambda x: int(x),
        os.popen('stty size', 'r').read().split()
    ))

    results_pad = curses.newpad(len(results) * 3, rows)
    # results_pad.refresh(0, 0, 0, 0, rows, cols)
    # stdscr.refresh()


if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.wrapper(main)
