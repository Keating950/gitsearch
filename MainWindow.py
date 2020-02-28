import curses
from collections import deque
from curses import textpad
from typing import List, Tuple, Dict, Union

Entry3 = Tuple[str, str, str]
Entry4 = Tuple[str, str, str, str]


class MainWindow:
    def __init__(self, stdscr: curses.window, results: List[dict]):
        self.stdscr = stdscr
        self.entry_pages = None
        self.QUARTER_LINES = curses.LINES // 4
        self.QUARTER_COLS = curses.COLS // 4
        self.HALF_LINES = curses.LINES // 2
        self.HALF_COLS = curses.COLS // 2
        self._pages = _make_pages(results)
        self._current_page = 0
        self.draw_page()
        self.stdscr.move(0, 0)
        self.windows = deque()

    def __getattr__(self, attr):
        return self.stdscr.__getattribute__(attr)

    def draw_page(self):
        pos = 0
        for entry in self._pages[self._current_page]:
            tmp_pos = pos
            self.addnstr(tmp_pos, 0, entry[0], curses.COLS - 1, curses.A_BOLD)
            tmp_pos += 1
            for i in range(1, len(entry)):
                self.addnstr(tmp_pos, 0, entry[i], curses.COLS - 1)
                tmp_pos += 1
            pos += len(entry)

    def turn_page(self, direction: int) -> bool:
        new_page = self._current_page + direction
        if (0 > new_page) or (new_page >= len(self._pages)):
            return False
        self._current_page = new_page
        self.erase()
        self.draw_page()
        return True

    def redraw_results(self) -> None:
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
        popup_window = curses.newwin(
            self.HALF_LINES, self.HALF_COLS, self.QUARTER_LINES, self.QUARTER_COLS
        )
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
        box = textpad.Textbox(input_window)
        curses.curs_set(1)
        popup_window.refresh()
        box.edit(key_validator)
        path = box.gather()
        curses.curs_set(0)
        del box
        del input_window
        popup_window.erase()
        # border is erased in prev call; redrawing
        popup_window.box()
        popup_window.addstr(
            self.QUARTER_LINES - 2, self.HALF_COLS // 2 - 5, "Cloning..."
        )
        popup_window.refresh()
        self.windows.append(popup_window)
        return path

    def clear_popup_win(self, repo: str, destination: str) -> None:
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
            self.HALF_LINES, self.HALF_COLS, self.QUARTER_LINES, self.QUARTER_COLS
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

    def move_highlight(self, prev_line_relative: int) -> None:
        # TODO: fix bug where bold is restored when scrolling up but not down
        y, _ = self.stdscr.getyx()
        is_bold = bool(self.stdscr.inch(y, 0) & curses.A_BOLD)
        if is_bold:
            self.stdscr.chgat(y + prev_line_relative, 0, curses.A_BOLD)
        else:
            self.stdscr.chgat(y + prev_line_relative, 0, curses.A_NORMAL)
        self.stdscr.chgat(y, 0, curses.A_STANDOUT)


def _make_pages(results: List[dict]):
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
    page_lines = 0
    pages = []
    page = []
    while entry_idx < len(entries):
        entry = entries[entry_idx]
        # leave 1 for bottom bar
        if page_lines + len(entry) < curses.LINES-1:
            page.append(entry)
            page_lines += len(entry)
            entry_idx += 1
        else:
            pages.append(page)
            page = []
            page_lines = 0
    return pages
