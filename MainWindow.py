import argparse
import curses
import re
from collections import deque
from curses import textpad
from typing import List, Tuple
from Entry import Entry
from EntryPages import EntryPages


class MainWindow:

    def __init__(self, stdscr: curses.window, formatted_args: argparse.Namespace,
                 entries: List[Entry]):
        self.stdscr = stdscr
        self.entry_pages = None
        self.QUARTER_LINES = curses.LINES // 4
        self.QUARTER_COLS = curses.COLS // 4
        self.HALF_LINES = curses.LINES // 2
        self.HALF_COLS = curses.COLS // 2
        self.entry_pages = EntryPages(entries, curses.LINES)
        self.entry_pages.draw_page(self.stdscr)
        self.stdscr.refresh()
        self.stdscr.move(0, 0)
        self.windows = deque()

    def is_url(self, text: str) -> bool:
        return bool(
            re.match(
                r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.["
                r"a-zA-Z0-9("
                r")]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&/=]*)",
                text)
        )

    def redraw_results(self):
        self.stdscr.erase()
        self.entry_pages.draw_page(self.stdscr)
        self.stdscr.refresh()

    def draw_textbox(self) -> str:
        def key_validator(key: int) -> int or None:
            # enter/return
            if key == 10:
                return 7
            elif key == 127:
                box.do_command(curses.KEY_BACKSPACE)
                return
            return key

        # Hierarchy:
        # popup_window: Visual container for prompt. Includes border.
        # input_window: single-line window. Kept empty other than textbox to keep
        #   gather() results clean.
        # box: Textbox object for actual editing.
        popup_window = curses.newwin(self.HALF_LINES, self.HALF_COLS,
                                     self.QUARTER_LINES,
                                     self.QUARTER_COLS)
        popup_window.box()
        popup_window.overlay(self.stdscr)
        # centering text by taking half_cols - ((length of phrase) // 2)
        popup_window.addstr(self.QUARTER_LINES - 2,
                            self.HALF_COLS // 2 - 14,
                            "Enter destination directory:"
                            )
        input_window = curses.newwin(1, self.HALF_COLS - 4,
                                     # just over halfway down popup_window
                                     self.QUARTER_LINES + self.HALF_LINES // 2,
                                     self.QUARTER_COLS + 2)
        box = textpad.Textbox(input_window)
        popup_window.refresh()
        box.edit(key_validator)
        path = box.gather()
        del box
        del input_window
        popup_window.erase()
        # border is erased in prev call; redrawing
        popup_window.box()
        popup_window.addstr(self.QUARTER_LINES - 2,
                            self.HALF_COLS // 2 - 5,
                            "Cloning..."
                            )
        popup_window.refresh()
        self.windows.append(popup_window)
        return path

    def clear_popup_win(self, repo: str, destination: str):
        success_msg = f"Cloned {repo} to {destination}."
        popup_window = self.windows.pop()
        popup_window.erase()
        popup_window.box()
        popup_window.addstr(self.QUARTER_LINES - 2,
                            self.HALF_COLS // 2 - len(success_msg) // 2,
                            success_msg)
        popup_window.refresh()
        # wait for keypress
        popup_window.getkey()
        popup_window.erase()
        del popup_window
        self.redraw_results()

    def draw_path_error_window(self, input_path: str) -> None:
        err_win = curses.newwin(self.HALF_LINES,
                                self.HALF_COLS,
                                self.QUARTER_LINES,
                                self.QUARTER_COLS)
        err_win.overlay(self.stdscr)
        err_win.box()
        err_win.addnstr(self.QUARTER_LINES - 2,
                        self.HALF_COLS // 2 - ((len(input_path) + 36) // 2),
                        f"{input_path} is not a valid path to a directory.",
                        self.HALF_COLS - 2)
        err_win.refresh()
        err_win.getkey()
        del err_win
        self.redraw_results()

    def input_stream(self) -> Tuple[str, str]:
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
                repo_url = self.stdscr.instr(y, 0).strip().decode("utf-8")
                if self.is_url(repo_url):
                    path = self.draw_textbox()
                    self.stdscr.touchwin()
                    return path, repo_url

            self.stdscr.refresh()
