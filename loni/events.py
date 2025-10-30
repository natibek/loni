
class MouseEvent:
    def __init__(self, x: int, y: int, bstate: int) -> None:
        self.x = x
        self.y = y
        self.bstate = bstate

class KeyEvent:
    def __init__(self, key: int) -> None:
        self.key = key
