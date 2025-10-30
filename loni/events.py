from __future__ import annotations
from typing import Protocol, Any, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from loni.widget import Widget

class Event:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.stop_propagation = False

    @property
    def widget(self) -> Widget:
        return self._widget

    @widget.setter
    def widget(self, widget: Widget) -> None:
        self._widget = widget

    def stop(self):
        self.stop_propagation = True

class MouseEvent(Event):
    def __init__(self, x: int, y: int, bstate: int) -> None:
        super().__init__(x, y)
        self.bstate = bstate

class KeyEvent(Event):
    def __init__(self, x: int, y: int, key: int) -> None:
        super().__init__(x, y)
        self.key = key

E = TypeVar("E", bound=Event, contravariant=True)
class EventHandlerType(Protocol[E]):
    def __call__(self, event: E, *args: Any, **kwargs: Any) -> None: ...
