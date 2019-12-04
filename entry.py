import curses


class Entry:

    def __init__(self, name: str, author: str, stars: int, url: str, lang: str = None,
                 descr: str = None):
        self.line0 = f"{name}\t{author}\t{lang if lang is not None else ''}\t{stars}"
        self.line1 = descr
        self.line2 = url
        if descr is not None:
            self.numlines = 3
        else:
            self.numlines = 2

    def print_lines(self, scrn, pos):
        tmp_pos = pos
        scrn.addnstr(tmp_pos, 0, self.line0, curses.COLS - 1, curses.A_BOLD)
        tmp_pos+=1
        if self.line1 is not None:
            scrn.addnstr(tmp_pos, 0, self.line1, curses.COLS - 1)
            tmp_pos+=1
        scrn.addnstr(tmp_pos, 0, self.line2, curses.COLS - 1)