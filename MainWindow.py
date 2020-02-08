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
        self.QUARTER_LINES = curses.LINES // 4
        self.QUARTER_COLS = curses.COLS // 4
        self.HALF_LINES = curses.LINES // 2
        self.HALF_COLS = curses.COLS // 2

    def draw_textbox(self, url: bytes or str):
        def validator(key):
            # enter/return
            if key == 10:
                return 7
            elif key == 127:
                box.do_command(curses.KEY_BACKSPACE)
                return
            return key

        # url matching regex
        if not re.match(
                r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.["
                r"a-zA-Z0-9("
                r")]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
                url.decode("utf-8")):
            return

        # Hierarchy:
        # popup_window: Visual container for prompt. Includes border.
        # input_window: single-line window. Kept empty other than textbox to keep
        #   gather() results clean.
        # box: Textbox object for actual editing.

        popup_window = curses.newwin(self.HALF_LINES, self.HALF_COLS,
                                     self.QUARTER_LINES,
                                     self.QUARTER_COLS)
        popup_window.overlay(self.stdscr)
        # unclear why i can only write to max_x-2 without err
        textpad.rectangle(popup_window, 0, 0,
                          popup_window.getmaxyx()[0] - 2,
                          popup_window.getmaxyx()[1] - 2)
        # centering text by taking half_cols - (len_of_phrase/2)
        popup_window.addstr(self.QUARTER_LINES - 1, self.HALF_COLS // 2 - 10,
                            "Enter path to clone:\n")
        # popup_window.move(self.QUARTER_LINES + 2, self.HALF_LINES + 1)
        box = textpad.Textbox(popup_window)
        popup_window.refresh()
        box.edit(validator)
        return box.gather()

    def input_stream(self):
        while True:
            y, x = self.stdscr.getyx()
            c = self.stdscr.getkey()
            if c == "j":
                if y + 1 < curses.LINES:
                    self.stdscr.move(y + 1, x)
            elif c == "k":
                if y - 1 >= 0:
                    self.stdscr.move(y - 1, x)
            elif c == "h":
                if x - 1 >= 0:
                    self.stdscr.move(y, x - 1)
            elif c == "l":
                if x + 1 <= curses.COLS:
                    self.stdscr.move(y, x + 1)
            elif c == "\t":
                self.entry_pages.turn_page(self.stdscr, 1)
                self.stdscr.move(y, x)
            elif c == "KEY_BTAB":
                self.entry_pages.turn_page(self.stdscr, -1)
                self.stdscr.move(y, x)
            elif c == "\n":
                repo_url = self.stdscr.instr(y, 0)
                path = self.draw_textbox(repo_url)

            self.stdscr.refresh()

    def main(self, formatted_args: argparse.Namespace):
        arg_str = ""
        for i in sys.argv:
            arg_str += str(i)
        entries = FetchResults.gen_entries(FetchResults.fetch(formatted_args))
        self.entry_pages = EntryPages(entries, curses.LINES)
        self.entry_pages.draw_page(self.stdscr)
        self.stdscr.refresh()
        self.stdscr.move(0, 0)

        try:
            self.input_stream()
        except KeyboardInterrupt:
            pass
        finally:
            curses.endwin()
