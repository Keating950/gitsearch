import FetchResults
from EntryPages import EntryPages
import argparse
import sys
import curses
from curses import textpad
import re


class MainWindow:

    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        self.entrypages = None

    def input_stream(self, entry_pages: EntryPages):
        idx = 0
        while True:
            y, x = curses.getsyx()
            c = self.stdscr.getkey()
            if c == "j":
                if y + 1 < curses.LINES:
                    self.stdscr.move(y + 1, x)
            elif c == "k":
                if y - 1 > 0:
                    self.stdscr.move(y - 1, x)
            elif c == "h":
                if x - 1 >= 0:
                    self.stdscr.move(y, x - 1)
            elif c == "l":
                if x + 1 < curses.COLS:
                    self.stdscr.move(y, x + 1)
            elif c == "\t":
                entry_pages.turn_page(self.stdscr, 1)
                self.stdscr.move(y, x)
            elif c == "KEY_BTAB":
                entry_pages.turn_page(self.stdscr, -1)
                self.stdscr.move(y, x)

            self.stdscr.refresh()

    def main(self, formatted_args: argparse.Namespace):
        arg_str = ""
        for i in sys.argv:
            arg_str += str(i)
        entries = FetchResults.gen_entries(FetchResults.fetch(formatted_args))
        self.entrypages = EntryPages(entries, curses.LINES)
        self.entrypages.draw_page(self.stdscr)
        self.stdscr.refresh()
        self.stdscr.move(0, 0)

        try:
            self.input_stream(self.entrypages)
        except KeyboardInterrupt:
            pass
        finally:
            curses.endwin()
