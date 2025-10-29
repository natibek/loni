import curses
from widget import Widget
from typing import Any, Callable

class LoniApp:
    __subs_for_mouse_event: dict[Widget, Callable[[int], None]] = {}
    __subs_for_key_event: dict[Widget, Callable[[int], None]] = {}

    def __init__(self) -> None:
       self.screen = curses.initscr()
       self.cur_window = self.screen

    def register_for_mouse_event(self, widget: Widget, callback: Callable[[int], None]) -> None:
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

    def key_event(self):
        (id, x, y, z, bstate) = curses.getmouse()

        for widget, callback in self.__subs_for_key_event.items():
            if widget.pos_in_box(x, y):
                callback(x, y, bstate)

    def event_loop(self) -> None:
        while True:
            if self.cur_window.getch():
                self.mouse_event()
                self.key_event()


