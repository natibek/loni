from __future__ import annotations

from typing import TYPE_CHECKING, Any
import curses

from loni.widget import Widget
from loni import _set_app
from loni.colors import Colors
from loni.events import MouseEvent, KeyEvent

if TYPE_CHECKING:
    from .events import EventHandlerType
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

        # update the global context with a new LoniApp
        _set_app(app)

        return app

    def __init__(self) -> None:
        stdscr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        self.colors = Colors()
        self.colors._generate_defaults()

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

    @classmethod
    def create_app(cls) -> tuple[LoniApp, Widget]:
        cls.__allow_direct_init = True
        app = cls()
        cls.__allow_direct_init = False
        return app, app.root

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



