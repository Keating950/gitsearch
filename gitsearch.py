import ResultFetcher
import sys
import curses
import os


def format_results(results: list) -> list:
    formatted = []
    # @formatter:off
    for repo in results:
        # codes in first line indicate to print in bold
        formatted.append(
            f"{repo['name']}    {repo['owner']['login']}    {repo['language']}    ☆{repo['stargazers_count']}"
            )
        formatted.append(repo['description'])
        formatted.append(repo['url'])
        formatted.append("\n")
    # @formatter:on
    return formatted


def init_pad(contents):
    pad = curses.newpad(len(contents)+1, curses.COLS)
    line_position = 0
    for idx, line in enumerate(contents):
        if line is not None:
            if idx%4==0:
                pad.addnstr(line_position, 0, line, curses.COLS - 1, curses.A_BOLD)
            else:
                pad.addnstr(line_position, 0, line, curses.COLS-1)
        else:
            pad.addnstr(line_position, 0, "\n", curses.COLS-1)
        line_position+=1
    pad.refresh(0, 0, 0, 0, curses.LINES-1, curses.COLS-1)
    return pad


def main(stdscr):
    arg_str = ""
    for i in sys.argv:
        arg_str += str(i)
    results = ResultFetcher.fetch_results()

    line_list = format_results(results)

    results_pad = init_pad(line_list)
    pad_pos = 0
    stdscr.refresh()

    while True:
        c = stdscr.getch()
        if c == ord("j"):
            pad_pos+=1
        if c == ord("k"):
            pad_pos-=1
        elif c == curses.KEY_DOWN:
            pass
        results_pad.refresh(pad_pos, 0, 0, 0, curses.LINES - 1, curses.COLS - 1)


if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.wrapper(main)
