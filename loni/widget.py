from __future__ import annotations
import curses

import enum

from loni.ctx import get_app

# maybe use strings
class BorderPos(enum.Enum):
    TOP_LEFT     = 0
    BOTTOM_LEFT  = 1
    TOP_CENTER   = 2
    BOTTOM_CENTER= 3
    TOP_RIGHT    = 4
    BOTTOM_RIGHT = 5


# TODO:
# 1: Padding and Marging
# 2: Redraw on screen resize
# 3: Container widgets with tkinter style packing
# 4: Scrolling containers
# 4: Custom widgets: switch, button, label, static, textarea, list, checkbox, h/v lines

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
        border_title: str = "",
        border_pos: BorderPos = BorderPos.TOP_LEFT,
        # padding: tuple[int, int] = (0, 0),
        **kwargs
    ) -> None:

        self.parent = parent

        if not parent: # we are creating the root box
            if self.__num_roots != 0:
                raise ValueError("Can not create more than one root Box. Pass the parent Box as an argument.")

            self.__num_roots += 1
            # Expect that curses.initscr() has been called and the resulting screen is passed as
            # a keyword argument.
            assert "stdscr" in kwargs and isinstance(kwargs["stdscr"], curses.window)
            self.parent_screen: curses.window = kwargs["stdscr"]
            self.parent_screen.clear()
            self.depth = 0
        else:
            self.parent_screen = parent.win
            self.depth = parent.depth + 1

        assert isinstance(self.parent_screen, curses.window)
        self.x = x
        self.y = y
        self.height = height or self.parent_screen.getmaxyx()[0]
        self.width = width or self.parent_screen.getmaxyx()[1]

        self.app = get_app()

        self.win = self.parent_screen.derwin(self.height, self.width, self.y, self.x)
        self.focus_bkgd = self.app.colors["WHITE_BLUE"]
        self.default_bkgd = self.app.colors["WHITE_GREEN"]

        self.win.bkgd(" ", self.default_bkgd)

        # for mouse presses
        self.win.keypad(True)
        self.win.nodelay(True)

    def remove_border(self) -> None:
        """Remove the border around the box"""
        self.win.border(1,1,1,1,1,1,1,1)

    def add_border(self) -> None:
        """:dd the border around the box"""
        self.win.border(0,0,0,0,0,0,0,0)


    @property
    def border(self) -> bool:
        return self._border

    @border.setter
    def border(self, border: bool) -> None:
        if border:
            self._border = True
            self.add_border()
            # self.win.box()
        else:
            self._border = False
            self.remove_border()


    def update_border_title(self, title: str, border_pos: BorderPos | None = None) -> None:
        """Write the border title."""
        # TODO: Include position arguments
        X_OFFSET = 3
        self.border_title = title

        if border_pos:
            self.border_pos = border_pos

        if not title:
            return

        if self.border_pos.value % 2 == 0:
            y = 0
        else:
            y = self.height - 1

        match self.border_pos:
            case BorderPos.TOP_LEFT | BorderPos.BOTTOM_LEFT:
                x = X_OFFSET
            case BorderPos.TOP_RIGHT | BorderPos.BOTTOM_RIGHT:
                x = max(0, self.width - X_OFFSET - len(title))
            case BorderPos.TOP_CENTER | BorderPos.BOTTOM_CENTER:
                x = max(0, (self.width // 2)  - (len(title) // 2))

        if len(title) >= self.width - x:
            title = title[:self.width - x]
        self.win.addstr(y, x, title)

    def draw(self) -> None:
        self.win.refresh()

class Widget(Box):
    """Interactive Box"""

    def __init__(
        self,
        parent: Box | None,
        x: int,
        y: int,
        height: int | None = None,
        width: int | None = None,
        border: bool = True,
        border_title: str = "",
        border_pos: BorderPos = BorderPos.TOP_LEFT,
        **kwargs
    ) -> None:
        super().__init__(parent, x, y, height, width, border, border_title, border_pos, **kwargs)

        self.border = border
        self.border_pos = border_pos
        self.update_border_title(border_title)

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

    # def update_text(self, txt: str) -> None:
    #     if not txt:
    #         return

    #     self.win.addstr(txt)

