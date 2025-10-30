import curses

class Colors:
    def __init__(self) -> None:
        self._colors: dict[str, int] = {}

    def __getitem__(self, color: str) -> int:
        if color in self._colors:
            return self._colors[color]

        raise AttributeError(f"Color '{color}' not found.")

    def _generate_defaults(self) -> None:
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        self._colors["WHITE_BLUE"] = curses.color_pair(1)

        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)
        self._colors["WHITE_GREEN"] = curses.color_pair(2)

