import curses
import os
from collections import namedtuple
from curses import textpad
from typing import List, Tuple, Dict, Union

Entry3 = Tuple[str, str, str]  # three-line entry
Entry4 = Tuple[str, str, str, str]  # four-line entry

# page: Tuple(List[Union[Entry3, Entry4]], Int)
Page = namedtuple("Page", ["entries", "last_line"])


class MainWindow:
    def __init__(self, stdscr, results: List[dict]):
        self.stdscr = stdscr
        self.QUARTER_LINES = curses.LINES // 4
        self.QUARTER_COLS = curses.COLS // 4
        self.HALF_LINES = curses.LINES // 2
        self.HALF_COLS = curses.COLS // 2
        self._pages = _make_pages(results)
        self._current_page_idx = 0
        self.draw_page()
        self.stdscr.move(0, 0)
        self.windows = []

    def __getattr__(self, attr):
        return self.stdscr.__getattribute__(attr)

    def draw_page(self) -> None:
        pos = 0
        for entry in self._pages[self._current_page_idx].entries:
            tmp_pos = pos
            self.addnstr(tmp_pos, 0, entry[0], curses.COLS - 1)
            tmp_pos += 1
            for i in range(1, len(entry)):
                self.addnstr(tmp_pos, 0, entry[i], curses.COLS - 1)
                tmp_pos += 1
            pos += len(entry)

    def turn_page(self, direction: int) -> bool:
        new_page = self._current_page_idx + direction
        if (0 > new_page) or (new_page >= len(self._pages)):
            return False
        self._current_page_idx = new_page
        self.erase()
        self.draw_page()
        return True

    def redraw_results(self) -> None:
        self.stdscr.erase()
        self.draw_page()
        self.stdscr.refresh()

    def move(self, y: int) -> None:
        y_current, _ = self.stdscr.getyx()
        if (0 > y) or (y > self._pages[self._current_page_idx].last_line):
            return
        self.stdscr.chgat(y_current, 0, curses.A_NORMAL)
        self.stdscr.chgat(y, 0, curses.A_STANDOUT)
        self.stdscr.move(y, 0)

    def path_prompt(self) -> str:

        def key_validator(key: int) -> int or None:
            if key == 10:  # enter/return
                return 7  # termination escape sequence
            elif key == 27:  # Esc key
                raise KeyboardInterrupt
            elif key == 127:
                box.do_command(curses.KEY_BACKSPACE)
            else:
                return key

        # Hierarchy:
        # popup_window: Visual container for prompt. Includes border.
        # input_window: single-line window. Kept empty other than textbox to keep
        #   gather() results clean.
        # box: Textbox object for actual editing.
        popup_window = curses.newwin(
            self.HALF_LINES, self.HALF_COLS, self.QUARTER_LINES,
            self.QUARTER_COLS
        )
        self.windows.append(popup_window)
        popup_window.box()
        popup_window.overlay(self.stdscr)
        # centering text by taking half_cols - ((length of phrase) // 2)
        popup_window.addstr(
            self.QUARTER_LINES - 2,
            self.HALF_COLS // 2 - 14,
            "Enter destination directory:",
        )
        input_window = curses.newwin(
            1,
            self.HALF_COLS - 4,
            # just over halfway down popup_window
            self.QUARTER_LINES + self.HALF_LINES // 2,
            self.QUARTER_COLS + 2,
        )
        default_path = os.getcwd().replace(os.path.expanduser("~"), "~") + "/"
        # max length is one fewer than input_window's width
        input_window.addnstr(0, 0, default_path, self.HALF_COLS - 5)
        box = textpad.Textbox(input_window)
        curses.curs_set(1)
        popup_window.refresh()
        try:
            box.edit(key_validator)
        except KeyboardInterrupt:
            popup_window.erase()
            self.redraw_results()
            return ''
        path = box.gather()
        curses.curs_set(0)
        popup_window.erase()
        # border is erased in prev call; redrawing
        popup_window.box()
        popup_window.addstr(
            self.QUARTER_LINES - 2, self.HALF_COLS // 2 - 5, "Cloning..."
        )
        popup_window.refresh()
        self.windows.append(popup_window)
        return path

    def draw_clone_success_msg(self, repo: str, destination: str) -> None:
        success_msg = f"Cloned {repo} to {destination}."
        popup_window = self.windows.pop()
        popup_window.erase()
        popup_window.box()
        popup_window.addstr(
            self.QUARTER_LINES - 2,
            self.HALF_COLS // 2 - len(success_msg) // 2,
            success_msg,
        )
        popup_window.refresh()
        # wait for keypress
        popup_window.getkey()
        popup_window.erase()
        del popup_window
        self.redraw_results()

    def draw_path_error_window(self, input_path: str) -> None:
        err_win = curses.newwin(
            self.HALF_LINES, self.HALF_COLS, self.QUARTER_LINES,
            self.QUARTER_COLS
        )
        err_win.overlay(self.stdscr)
        err_win.box()
        err_win.addnstr(
            self.QUARTER_LINES - 2,
            self.HALF_COLS // 2 - ((len(input_path) + 36) // 2),
            f"{input_path} is not a valid path to a directory.",
            self.HALF_COLS - 2,
        )
        err_win.refresh()
        err_win.getkey()
        del err_win
        self.redraw_results()


def _make_pages(results: List[dict]) -> List[Page]:
    def make_entry(repo: Dict[str, Union[str, dict]]) -> Union[Entry3, Entry4]:
        title_str = f"{repo['name']}\t" \
                    f"{repo['owner']['login']}\t" \
                    f"{repo.get('lang') + '   ' if repo.get('lang') is not None else ''}" \
                    f"{repo['stargazers_count']}"
        desc = repo.get("description")
        url = repo["url"]
        if desc:
            return title_str, desc, url, "\n"
        return title_str, url, "\n"

    entries = [make_entry(repo) for repo in results]
    entry_idx = 0
    nlines = 0
    pages = []
    page_contents = []
    while entry_idx < len(entries):
        entry = entries[entry_idx]
        # leave 1 for bottom bar
        if nlines + len(entry) < curses.LINES - 1:
            page_contents.append(entry)
            # account for zero-indexing
            nlines += len(entry) - 1
            entry_idx += 1
        else:
            pages.append(Page(page_contents, nlines))
            page_contents = []
            nlines = 0
    return pages
