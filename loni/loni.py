from __future__ import annotations

import curses
from widget import Widget
from events import MouseEvent, KeyEvent
from typing import Callable

def initialize_colors() -> None:
    """Initializes the colors to be used. Called when the root box is created."""

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)

class LoniApp:
    __subs_for_mouse_event: dict[Widget, Callable[[MouseEvent], None]] = {}
    __subs_for_key_event: dict[Widget, Callable[[KeyEvent], None]] = {}

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
        stdscr = curses.initscr()
        initialize_colors()

        self.root= Widget(None, 0, 0, stdscr = stdscr)

        curses.curs_set(0)

        # defaults
        curses.cbreak()
        curses.noecho()
        curses.flushinp()

        # enable mouse
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

        self.cur_window = self.root
        self.register_for_mouse_event(self.root, lambda _: None)

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

    def register_for_mouse_event(self, widget: Widget, callback: Callable[[MouseEvent], None]) -> None:
        self.__subs_for_mouse_event[widget] = callback

    def register_for_key_event(self, widget: Widget, callback: Callable[[KeyEvent], None]) -> None:
        self.__subs_for_key_event[widget] = callback

    def mouse_event(self):
        (_, x, y, _, bstate) = curses.getmouse()
        event = MouseEvent(x, y, bstate)

        widgets_containing_mouse: list[tuple[Widget, Callable[[MouseEvent], None]]] = []
        if bstate & curses.BUTTON1_CLICKED:
            for widget, callback in self.__subs_for_mouse_event.items():
                # find all the widgets that enclose the location of the mouse event
                if widget.win.enclose(y, x):
                    widgets_containing_mouse.append((widget, callback))


        if not widgets_containing_mouse:
            return

        # sort the widgets by their depth in reverse order
        # TODO: handle overlapping widgets
        widgets_containing_mouse.sort(key=lambda tup: tup[0].depth, reverse=True)

        focused = False
        for widget, callback in widgets_containing_mouse:
            if not focused and widget.focusable:
                self.in_focus = widget
                focused = True

            if not event.stop_propagation:
                callback(event)

    def key_event(self, char: int):
        event = KeyEvent(char)
        for widget, callback in self.__subs_for_key_event.items():
            callback(event)

    def exit(self) -> None:
        curses.nocbreak()
        self.root.win.keypad(False)
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
                self.root.win.addch(chr(char))
                self.key_event(char)

            self.cur_window.win.refresh()

def do_nothing(event):
    event.stop()

def main() -> None:
    app, root = LoniApp.create_app()

    try:
        box = Widget(root, 10, 10, 20, 20)
        app.register_for_mouse_event(box, do_nothing)

        box2 = Widget(root, 20, 10, 20, 20)
        app.register_for_mouse_event(box2, do_nothing)

        box3 = Widget(box2, 10, 10, 5, 8)
        app.register_for_mouse_event(box3, do_nothing)

        app.event_loop()
    except Exception as e:
        app.exit()
        raise e

if __name__ == "__main__":
    SystemExit(main())



