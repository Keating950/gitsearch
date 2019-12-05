from entry import Entry
import ResultFetcher
import sys
import curses


def make_entry_objects(results: list) -> list:
    entries = []
    for repo in results:
        # codes in first line indicate to print in bold
        entry = Entry(repo['name'], repo['owner']['login'], int(repo['stargazers_count']),
                      repo['url'], repo.get('language'), repo.get('description'),
                      )
        entries.append(entry)
    return entries


def init_pad(contents):
    # each entry's length + space for a newline + 1 to account for zero-indexing
    sumlines = sum([entry.numlines for entry in contents]) + len(contents) + 1
    pad = curses.newpad(sumlines, curses.COLS)
    line_position = 0
    for entry in contents:
        entry.print_lines(pad, line_position)
        line_position += entry.numlines
        pad.addch(line_position, 0, "\n")
        line_position += 1
    pad.refresh(0, 0, 0, 0, curses.LINES - 1, curses.COLS - 1)
    return pad


def input_stream(pad, pad_max_y: int):
    pad_pos = 0
    curs_y, curs_x = curses.getsyx()
    stdscr.refresh()

    while True:
        c = stdscr.getch()
        if c == ord("j"):
            pad_pos += 1
        elif c == ord("k"):
            pad_pos -= 1

        elif c in {curses.KEY_DOWN, curses.KEY_UP}:
            y, x = curses.getsyx()
            if c == curses.KEY_DOWN:
                if y == curses.LINES - 1:
                    pad_pos += 1
                else:
                    curses.setsyx(y + 1, x)

            elif c == curses.KEY_UP:
                if y == 0:
                    if pad_pos > 0:
                        pad_pos -= 1
                    else:
                        pass
                else:
                    curses.setsyx(y - 1, x)

        elif c in {curses.KEY_LEFT, curses.KEY_RIGHT}:
            y, x = curses.getsyx()
            if c == curses.KEY_LEFT:
                if x - 1 < 0:
                    pass
                else:
                    curses.setsyx(y, x - 1)
            elif c == curses.KEY_RIGHT:
                if x + 1 > curses.COLS - 1:
                    pass
                else:
                    curses.setsyx(y, x + 1)
        if pad_pos < pad_max_y:
            pad.refresh(pad_pos, 0, 0, 0, curses.LINES - 1, curses.COLS - 1)
        else:
            pad_pos = pad_max_y


def main(stdscr):
    arg_str = ""
    for i in sys.argv:
        arg_str += str(i)
    results = ResultFetcher.fetch_results()

    entry_list = make_entry_objects(results)

    results_pad = init_pad(entry_list)
    pad_max_y = sum([entry.numlines for entry in entry_list]) + len(entry_list) + 1
    input_stream(results_pad, pad_max_y)


if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.wrapper(main)
