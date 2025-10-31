from loni.widget import Widget, Box, BorderPos
from loni.widgets.utils import calculate_text_size
from loni.ctx import get_app

# TODO: 9 alignment options for text as well as padding/margin

class Label(Widget):
    def __init__(
        self,
        parent: Box,
        x: int,
        y: int,
        height: int | None = None,
        width: int | None = None,
        border: bool = True,
        border_title: str = "",
        border_pos: BorderPos = BorderPos.TOP_LEFT,
        text: str = "",
        grow_size_only: bool = False,
        **kwargs
    ) -> None:
        assert isinstance(text, str)
        self.parent_win = parent.win
        self.depth = parent.depth + 1
        self.app = get_app()

        self.x = x
        self.y = y

        self.text = text
        self.text_size = calculate_text_size(text)

        if height:
            self.height = self.text_size[0] + 2 if self.text_size[0] + 2 > height else height
        else:
            self.height = self.text_size[0] + 2

        if width:
            self.width = self.text_size[1] + 2 if self.text_size[1] + 2 > width else width
        else:
            self.width = self.text_size[1] + 2

        self.grow_size_only = grow_size_only

        self.win = self.parent_win.derwin(self.height, self.width, self.y, self.x)
        self.win.overlay(self.parent_win)
        self.focus_bkgd = self.app.colors["WHITE_BLUE"]
        self.default_bkgd = self.app.colors["WHITE_GREEN"]

        self.win.bkgd(" ", self.default_bkgd)

        # for mouse presses
        self.win.keypad(True)
        self.win.nodelay(True)

        self.border = border
        self.border_pos = border_pos
        self.border_title = border_title
        # self.update_border_title(border_title)

        self.focusable = True
        # This will help with widgets for which it doesn't make sense for events to propagate
        # eg Buttons for mouse event
        self.propagates_mouse_event = True
        self.propagates_key_event = True

        self.update_border_title(f"{self.height},{self.width}")

        self.write_text(self.text)

    def write_text(self, text: str) -> None:
        for row, txt in enumerate(text.split("\n")):
            self.win.addstr(1 + row, 1, txt)

        self.win.refresh()

    def update_size(self, text: str, grow_size_only: bool | None = None) -> None:
        """Update the size of the label given the new input.

        """
        if grow_size_only is not None:
            self.grow_size_only = grow_size_only

        if text == self.text:
            return

        text_size = calculate_text_size(text)

        if text_size == self.text_size:
            return

        self.text_size = text_size
        if self.grow_size_only:
            new_height = self.text_size[0] + 2 if self.text_size[0] + 2 > self.height else self.height
            new_width = self.text_size[1] + 2 if self.text_size[1] + 2 > self.width else self.width
        else:
            new_height = self.text_size[0] + 2
            new_width = self.text_size[1] + 2

        if new_height == self.height and new_width == self.width:
            return

        self.height, self.width = new_height, new_width

        self.win.erase()
        self.parent_win.redrawwin()
        self.parent_win.refresh()
        self.win.resize(self.height, self.width)
        self.win.refresh()

        if self.border:
            self.add_border()

            self.update_border_title(f"{self.height},{self.width}")

    def update_text(self, text: str) -> None:
        if not text:
            return

        self.update_size(text)
        self.write_text(text)
        self.win.refresh()

