from __future__ import annotations

import curses
from widget import Widget
from events import MouseEvent, KeyEvent, EventHandlerType, Event
from typing import Any

def initialize_colors() -> None:
    """Initializes the colors to be used. Called when the root box is created."""

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)


EventCallBackAndArgs = tuple[EventHandlerType | None, tuple[Any, ...], dict[str, Any]]

class LoniApp:
    __subs_for_mouse_event: dict[Widget, EventCallBackAndArgs] = {}
    __subs_for_key_event: dict[Widget, EventCallBackAndArgs] = {}

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
        self.register_for_mouse_event(self.root)

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

    def register_for_mouse_event(
        self,
        widget: Widget,
        callback: EventHandlerType | None = None,
        args: tuple[Any, ...] = tuple(),
        kwargs: dict[str, Any] = {},
    ) -> None:

        self.__subs_for_mouse_event[widget] = (callback, args, kwargs)

    def register_for_key_event(
        self,
        widget: Widget,
        callback: EventHandlerType | None = None,
        args: tuple[Any, ...] = tuple(),
        kwargs: dict[str, Any] = {},
    ) -> None:
        self.__subs_for_key_event[widget] = (callback, args, kwargs)

    def mouse_event(self):
        """Handle the mouse event by findings all the widgets that enclose the event that have
        registered for the event and calling their callback function.
        """
        (_, x, y, _, bstate) = curses.getmouse()
        event = MouseEvent(x, y, bstate)

        widgets_containing_mouse: list[tuple[Widget, EventCallBackAndArgs]] = []
        if bstate & curses.BUTTON1_CLICKED:
            for widget, callback_and_args in self.__subs_for_mouse_event.items():
                # find all the widgets that enclose the location of the mouse event
                if widget.win.enclose(y, x):
                    widgets_containing_mouse.append((widget, callback_and_args))


        if not widgets_containing_mouse:
            return

        # sort the widgets by their depth in reverse order
        # TODO: handle overlapping widgets
        widgets_containing_mouse.sort(key=lambda tup: tup[0].depth, reverse=True)

        focused = False
        for widget, callback_and_args in widgets_containing_mouse:
            if not focused and widget.focusable:
                self.in_focus = widget
                focused = True

            if not event.stop_propagation:
                event.widget = widget
                callback, args, kwargs = callback_and_args

                if callback is None:
                    continue

                callback(event, *args, **kwargs)
                if not widget.propagates_mouse_event:
                    event.stop()


    def key_event(self, char: int):
        """Handle the key inputs by findings all the widgets that enclose the cursor that have
        registered for the event and calling their callback function.
        """
        y, x = self.root.win.getyx()
        event = KeyEvent(x, y, char)

        widgets_containing_cursor: list[tuple[Widget, EventCallBackAndArgs]] = []

        for widget, callback_and_args in self.__subs_for_key_event.items():
            if widget.win.enclose(y, x):
                widgets_containing_cursor.append((widget, callback_and_args))

        if not widgets_containing_cursor:
            return

        widgets_containing_cursor.sort(key=lambda tup: tup[0].depth, reverse=True)
        for widget, callback_and_args in widgets_containing_cursor:
            if not event.stop_propagation:
                event.widget = widget
                callback, args, kwargs = callback_and_args
                if callback is None:
                    continue
                callback(event, *args, **kwargs)
                if not widget.propagates_key_event:
                    event.stop()


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

def do_nothing(event: Event):
    event.stop()

def update_title(event: MouseEvent, *args, **kwargs) -> None:
    return

def handle_key(event: KeyEvent) -> None:
    me = event.widget
    me.update_text(f"Key pressed {chr(event.key)}")


def main() -> None:
    app, root = LoniApp.create_app()
    root.update_border_title("HOME")
    try:
        box = Widget(root, 10, 10, 20, 20, border_title="Border 1")
        app.register_for_mouse_event(box, do_nothing)
        app.register_for_key_event(box, update_title)

        box2 = Widget(root, 20, 10, 20, 20)
        app.register_for_mouse_event(box2, do_nothing)

        box3 = Widget(box2, 10, 10, 5, 8)
        app.register_for_mouse_event(box3, lambda event: root.update_border_title("Pressed"))

        app.event_loop()
    except Exception as e:
        app.exit()
        raise e

if __name__ == "__main__":
    SystemExit(main())



