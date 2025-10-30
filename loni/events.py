
class MouseEvent:
    def __init__(self, x: int, y: int, bstate: int) -> None:
        self.x = x
        self.y = y
        self.bstate = bstate
        self.stop_propagation = False

    def stop(self):
        self.stop_propagation = True

class KeyEvent:
    def __init__(self, key: int) -> None:
        self.key = key
        self.stop_propagation = False

    def stop(self):
        self.stop_propagation = True
