import curses

class Box:
    """Defines what it is to occupy space on a screen."""

    def __init__(self, x: int, y: int, height: int, width: int, parent_screen: curses.window) -> None:
        self.stdsrc = parent_screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def mouse_pressed(self) -> None:
        pass

    def pos_in_box(self, x: int, y: int) -> bool:
        """Check if the given x and y coordinates are in the box.

        """
        return (self.x <= x < self.width - self.x) and (self.y <= y < self.height - self.y)


class Widget(Box):
    def __init__(self, x: int, y: int, height: int, width: int, parent_screen: curses.window) -> None:
        super().__init__(x, y, height, width, parent_screen)
        self.focusable = True

    def focus(self) -> None:
        pass
