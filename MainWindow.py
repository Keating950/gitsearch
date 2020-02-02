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
        self.entry_pages = None

    def draw_textbox(self, url: bytes or str):

        def validator()

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
            input_window = curses.newwin(half_lines, half_cols, quarter_lines,
                                         quarter_cols)
            textpad.rectangle(self.stdscr, quarter_lines - 1, quarter_cols - 1,
                              int(half_lines * 1.5) + 1,
                              int(half_cols * 1.5) + 1)
            # centering text by taking half_cols - (len_of_phrase/2)
            input_window.addstr(quarter_lines - 1, half_cols // 2 - 10,
                                "Enter path to clone:\n")
            # input_window.addstr(quarter_lines + 2,
            #                     f"{' ' * (half_lines - 1)}", curses.A_UNDERLINE)
            input_window.move(quarter_lines + 2, half_lines + 1)
            self.stdscr.refresh()
            input_window.refresh()
            box = textpad.Textbox(input_window)
            box.edit()
            return box.gather()

    def input_stream(self):
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
                self.entry_pages.turn_page(self.stdscr, 1)
                self.stdscr.move(y, x)
            elif c == "KEY_BTAB":
                self.entry_pages.turn_page(self.stdscr, -1)
                self.stdscr.move(y, x)
            elif c == "\n":
                # self.stdscr.nodelay(1)
                foo = self.stdscr.instr(y, 0)
                # self.stdscr.nodelay(0)
                self.draw_textbox(foo)

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
            self.input_stream()
        except KeyboardInterrupt:
            pass
        finally:
            curses.endwin()
