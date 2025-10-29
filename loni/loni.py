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
            assert isinstance(app, LoniApp)

        return app

    def __init__(self) -> None:
        self.stdscr = curses.initscr()

        self.root= Widget(self.stdscr, 0, 0)
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.noecho()

        self.cur_window = self.root

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

        for widget, callback in self.__subs_for_mouse_event.items():
            if widget.pos_in_box(x, y):
                if widget.focusable:
                    widget.focus()

                callback(x, y, bstate)

    def key_event(self, char: int):
        for widget, callback in self.__subs_for_key_event.items():
            callback(char)

    def exit(self) -> None:
        assert self.stdscr
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def event_loop(self) -> None:
        assert self.root
        while True:
            char = self.cur_window.win.getch()
            if char == curses.ERR:
                continue

            if "q" == chr(char):
                self.exit()
                break

            if char == curses.KEY_MOUSE:
                self.mouse_event()
            else:
                self.key_event(char)



def main() -> None:
    app, root = LoniApp.create_app()
    box = Widget(root.win, 10, 10, 20, 20)

    app.event_loop()

if __name__ == "__main__":
    SystemExit(main())



