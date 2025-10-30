from __future__ import annotations
import curses

class Box:
    """Defines what it is to occupy space on a screen."""

    __num_roots: int = 0
    def __init__(
        self,
        parent: Box | None,
        x: int,
        y: int,
        height: int | None = None,
        width: int | None = None,
        border: bool = True,
        **kwargs
    ) -> None:

        self.parent = parent

        if not parent: # we are creating the root box
            if self.__num_roots != 0:
                raise ValueError("Can not create more than one root Box. Pass the parent Box as an argument.")

            self.__num_roots += 1
            # Expect that curses.initscr() has been called and the resulting screen is passed as
            # a keyword argument.
            assert "stdscr" in kwargs
            self.parent_screen = kwargs["stdscr"]
            self.depth = 0
        else:
            self.parent_screen = parent.win
            self.depth = parent.depth + 1

        assert isinstance(self.parent_screen, curses.window)
        self.x = x
        self.y = y
        self.height = height or self.parent_screen.getmaxyx()[0]
        self.width = width or self.parent_screen.getmaxyx()[1]
        self.win = self.parent_screen.derwin(self.height, self.width, self.y, self.x)

        self.focus_bkgd = curses.color_pair(1)
        self.default_bkgd = curses.color_pair(2)

        self.win.bkgd(" ", self.default_bkgd)

        # for mouse presses
        self.win.keypad(True)
        self.win.nodelay(True)

        if border:
            self.win.box()

class Widget(Box):

    def __init__(
        self,
        parent: Box | None,
        x: int,
        y: int,
        height: int | None = None,
        width: int | None = None,
        border: bool = True,
        **kwargs
    ) -> None:
        super().__init__(parent, x, y, height, width, border, **kwargs)
        self.focusable = True

        # This will help with widgets for which it doesn't make sense for events to propagate
        # eg Buttons for mouse event
        self.propagates_mouse_event = True
        self.propagates_key_event = True

    def focus(self) -> None:
        if self.focusable:
            self.win.bkgd(" ", self.focus_bkgd)

    def defocus(self) -> None:
        self.win.bkgd(" ", self.default_bkgd)

    def update_text(self, txt: str) -> None:
        if not txt:
            return

        self.win.addstr(txt)

