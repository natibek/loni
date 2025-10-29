from __future__ import annotations

import curses
from widget import Widget
from typing import Callable

class LoniApp:
    __subs_for_mouse_event: dict[Widget, Callable[[int, int, int], None]] = {}
    __subs_for_key_event: dict[Widget, Callable[[int], None]] = {}

    __allow_direct_init = False
    __inst: LoniApp | None = None

    def __new__(cls) -> LoniApp:
        if not cls.__allow_direct_init:
            raise Exception("Use `LoniApp.create_app()` to create the app.")

        if cls.__inst is None:
            app = super().__new__(cls)
        else:
            app = cls.__inst

        return app

    def __init__(self) -> None:
        self.stdscr = curses.initscr()

        # some initial colors
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)


        self.root= Widget(self.stdscr, 0, 0)


        curses.curs_set(0)
        # defaults
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.noecho()
        self.stdscr.nodelay(True)
        curses.flushinp()

        # enable mouse
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

        self.cur_window = self.root
        self.register_for_mouse_event(self.root, self.root.mouse_pressed)

    @property
    def in_focus(self) -> Widget:
        return self._in_focus

    @in_focus.setter
    def in_focus(self, widget: Widget) -> None:
        if not widget.focusable:
            return

        if hasattr(self, "_in_focus"):
            self._in_focus.defocus()

        widget.focus()
        self._in_focus = widget

    @classmethod
    def create_app(cls) -> tuple[LoniApp, Widget]:
        cls.__allow_direct_init = True
        app = cls()
        cls.__allow_direct_init = False
        return app, app.root

    def register_for_mouse_event(self, widget: Widget, callback: Callable[[int, int, int], None]) -> None:
        self.__subs_for_mouse_event[widget] = callback

    def register_for_key_event(self, widget: Widget, callback: Callable[[int], None]) -> None:
        self.__subs_for_key_event[widget] = callback

    def mouse_event(self):
        (id, x, y, z, bstate) = curses.getmouse()

        if bstate & curses.BUTTON1_CLICKED:
            for widget, callback in self.__subs_for_mouse_event.items():
                if widget.win.enclose(y, x):
                    if widget.focusable:
                        self.in_focus = widget

                    callback(x, y, bstate)

    def key_event(self, char: int):
        for widget, callback in self.__subs_for_key_event.items():
            callback(char)

    def exit(self) -> None:
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        curses.flushinp()

    def event_loop(self) -> None:
        while True:
            char = self.cur_window.win.getch()
            if char == -1:
                continue

            if "q" == chr(char):
                self.exit()
                break

            if char == curses.KEY_MOUSE:
                self.mouse_event()
            else:
                self.stdscr.addch(chr(char))
                self.key_event(char)

            self.cur_window.win.refresh()



def main() -> None:
    app, root = LoniApp.create_app()
    box = Widget(root.win, 10, 10, 20, 20)
    app.register_for_mouse_event(box, box.mouse_pressed)

    box2 = Widget(root.win, 40, 10, 20, 20)
    app.register_for_mouse_event(box2, box2.mouse_pressed)

    app.event_loop()

if __name__ == "__main__":
    SystemExit(main())



