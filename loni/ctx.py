from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from loni.loniapp import LoniApp

# Global context for the running app
app: "LoniApp | None" = None

def get_app() -> "LoniApp":
    if _app is None:
        raise RuntimeError("LoniApp has not been created yet.")
    return _app

def _set_app(app: "LoniApp") -> None:
    global _app
    _app = app
