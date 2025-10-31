from loni import LoniApp
from loni.widget import BorderPos, Widget
from loni.events import MouseEvent, Event, KeyEvent
from loni.widgets.label import Label

def do_nothing(event: Event):
    event.stop()

def update_title(event: MouseEvent, *args, **kwargs) -> None:
    return

def handle_key(event: KeyEvent) -> None:
    widget = event.widget
    assert isinstance(widget, Label)
    widget.update_text("Ahhhhhhh!\n"*5)


def main() -> None:
    app, root = LoniApp.create_app()
    try:
        root.border = False
        root.update_border_title("HOME", BorderPos.TOP_CENTER)

        # box = Widget(root, 10, 10, 20, 20)
        # app.register_for_mouse_event(box, do_nothing)
        # app.register_for_key_event(box, update_title)
        # box.draw()

        box2 = Widget(root, 20, 10, 20, 20, border_title="Box 2", border_pos=BorderPos.BOTTOM_CENTER)
        app.register_for_mouse_event(box2, do_nothing)

        # box3 = Widget(box2, 10, 10, 5, 8)
        # app.register_for_mouse_event(box3, lambda event: root.update_border_title("Pressed", BorderPos.BOTTOM_CENTER))
        label = Label(root, 10, 10, text="What is your name?\nMy name is the man that")
        app.register_for_key_event(label,handle_key)
        app.event_loop()

    except Exception as e:
        app.exit()
        raise e

if __name__ == "__main__":
    SystemExit(main())
