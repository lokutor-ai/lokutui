# Lokutui

Lokutui is a lightweight Python library for building native terminal user interfaces (TUIs) using `curses`. It provides core screen management, an event system, and a collection of common widgets that can be composed to build interactive text‑based applications.

## Installation

Lokutui is distributed via PyPI;

```sh
pip install lokutui
```

Alternatively, include it directly as a dependency in your project or install from source.

## Core concepts

### Screen

`Screen` is the entry point for any application. It handles curses initialization, the main loop, input polling, rendering, and event dispatching. Typical usage:

```python
from lokutui.core import Screen

screen = Screen()

# add widgets
# screen.add_widget(my_widget)

screen.run()
```

The `run` method accepts an optional `initial_setup_callback` where you can configure widgets before the loop starts. Call `screen.exit()` from any handler to terminate the application.

`Screen` also supports a simple loading overlay and a modal widget you can assign to `screen.modal`.

### Widget

All visual elements inherit from the base `Widget` class. A widget has position (`x`, `y`), optional size (`width`, `height`), and visibility. Widgets must implement `render(stdscr, max_y, max_x)` and may override `handle_event(event)` to react to input.

## Event system

Events are instances of a simple named tuple with `type` and `data`. The library provides helpers for creating key, mouse and custom events:

```python
from lokutui.events import create_key_event, CustomEvent
```

`EventDispatcher` is a singleton used by the screen to dispatch events to registered handlers. You can register handlers and post events either directly or by using the global queue:

```python
from lokutui.events import EventDispatcher

dispatcher = EventDispatcher()
def on_key(e):
    ...
dispatcher.register_handler('key', on_key)
```

Handlers are called for each event type when `Screen` processes the queue.

## Widgets

Lokutui includes a number of built‑in widgets located in `lokutui.widgets`:

- **Label** – render static text at a position with optional width and color.
- **Box** – draw a bordered rectangle.
- **Frame** – a `Box` with an optional title.
- **Button** – clickable text; supports focus/highlight and invokes an `on_click` callback.
- **TextInput** – single‑line editable input field with basic cursor movement and text editing.
- **List** – scrollable list of strings; arrow keys or `j`/`k` to navigate, `ENTER` to select.
- **Select** – horizontal chooser cycling through options with left/right or `h`/`l` keys.
- **Checkbox** – toggleable checkbox with label.
- **VStack/HStack** – layout containers stacking child widgets vertically or horizontally.
- **Dialog** – simple yes/no modal dialog.
- **FormDialog** – multi‑field modal form with save/cancel buttons.
- **LogDisplay** – scrollable log window for output messages.
- **ProgressBar** – horizontal progress indicator.
- **Chart** – very basic line chart using braille characters.

Each widget accepts positioning and sizing arguments, color pair indices for `curses` attributes, and optional callbacks for interactions (`on_click`, `on_select`, `on_change`, etc.).

Example of building a simple form:

```python
from lokutui.core import Screen
from lokutui.widgets import VStack, Label, TextInput, Button

screen = Screen()

name_input = TextInput(x=2, y=2, width=20)
submit = Button("Submit", x=2, y=4, on_click=lambda: screen.exit())

vstack = VStack([Label("Name:"), name_input, submit], x=1, y=1, spacing=1)
screen.add_widget(vstack)

screen.run()
```

## Extending Lokutui

You can subclass `Widget` to create custom components. Implement rendering logic and event handling as needed and add instances to the `Screen`.

## Contributing

Contributions are welcome. Please open issues or pull requests in the repository and follow standard Python packaging conventions.

## License

MIT
