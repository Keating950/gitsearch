import curses


class Entry:
    def __init__(
        self,
        name: str,
        author: str,
        stars: int,
        url: str,
        lang: str = None,
        description: str = None,
    ):
        self.line0 = f"{name}\t{author}\t{lang if lang is not None else ''}\t{stars}"
        self.line1 = description
        self.line2 = url
        self.spacer = "\n"
        if description is not None:
            self.numlines = 4
        else:
            self.numlines = 3

    def draw(self, screen: curses.window, pos):
        tmp_pos = pos
        screen.addnstr(tmp_pos, 0, self.line0, curses.COLS - 1)
        tmp_pos += 1
        if self.line1 is not None:
            screen.addnstr(tmp_pos, 0, self.line1, curses.COLS - 1)
            tmp_pos += 1
        screen.addnstr(tmp_pos, 0, self.line2, curses.COLS - 1)
        tmp_pos += 1
        screen.addstr(tmp_pos, 0, self.spacer)
