import curses
from typing import List
from Entry import Entry


class EntryPages:

    def __init__(self, entries: List[Entry], line_limit: int):
        self._pages = []
        self.current_page = 0
        entry_idx = 0
        page = []
        page_lines = 0
        while entry_idx < len(entries):
            entry = entries[entry_idx]
            if page_lines + entry.numlines < line_limit:
                page.append(entry)
                page_lines += entry.numlines
                entry_idx += 1
            else:
                self._pages.append(page)
                page = []
                page_lines = 0

    def draw_page(self, screen: curses.window):
        pos = 0
        for entry in self._pages[self.current_page]:
            entry.draw(screen, pos)
            pos += entry.numlines

    def turn_page(self, screen: curses.window, direction: int):
        page = self.current_page + direction
        pos = 0
        if page <= len(self._pages):
            for entry in self._pages[page]:
                entry.draw(screen, pos)
                pos += entry.numlines
