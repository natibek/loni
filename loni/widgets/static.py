from loni.widget import Widget, Box, BorderPos
from loni.widgets.utils import calculate_text_size
from loni.ctx import get_app

class Static(Widget):
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
        **kwargs
    ) -> None:
        assert isinstance(text, str)
        self.parent_screen = parent.win
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

        self.win = self.parent_screen.derwin(self.height, self.width, self.y, self.x)
        self.focus_bkgd = self.app.colors["WHITE_BLUE"]
        self.default_bkgd = self.app.colors["WHITE_GREEN"]

        self.win.bkgd(" ", self.default_bkgd)

        # for mouse presses
        self.win.keypad(True)
        self.win.nodelay(True)

        self.border = border
        self.border_pos = border_pos
        # self.update_border_title(border_title)

        self.update_border_title(f"{self.height},{self.width}")

        self.update_text(self.text)

    def update_text(self, text: str) -> None:
        if not text:
            return
        self.text_size = calculate_text_size(text)

        for row, txt in enumerate(text.split("\n")):
            self.win.addstr(1 + row, 1, txt)

        self.win.refresh()

