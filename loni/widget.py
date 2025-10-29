from __future__ import annotations
import curses

class Box:
    """Defines what it is to occupy space on a screen."""

    def __init__(self, parent_screen: curses.window, x: int, y: int, height: int | None = None, width: int | None = None) -> None:
        self.parent_screen = parent_screen
        self.x = x
        self.y = y
        self.height = height or parent_screen.getmaxyx()[0]
        self.width = width or parent_screen.getmaxyx()[1]
        self.win = self.parent_screen.derwin(self.height, self.width, self.y, self.x)

        self.default_bkgd = curses.color_pair(2)

        self.win.bkgd(" ", self.default_bkgd)
        # for mouse presses
        self.win.keypad(True)
        self.win.nodelay(True)

        self.win.box()

    def mouse_pressed(self, x: int, y: int, bstate: int) -> None:
        pass

    def pos_in_box(self, x: int, y: int) -> bool:
        """Check if the given x and y coordinates are in the box.

        """
        return (self.x <= x < self.width - self.x) and (self.y <= y < self.height - self.y)


class Widget(Box):
    def __init__(self, parent_screen: curses.window, x: int, y: int, height: int | None = None, width: int | None = None) -> None:
        super().__init__(parent_screen, x, y, height, width)
        self.focusable = True


    def focus(self) -> None:
        self.win.bkgd(" ", curses.color_pair(1))

    def defocus(self) -> None:
        self.win.bkgd(" ", self.default_bkgd)

    def update_text(self, txt: str) -> None:
        if not txt:
            return
