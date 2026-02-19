import curses
import time
from collections import deque
from lokutui.events import EventDispatcher, create_key_event, _global_event_queue


class Screen:
    """Manages the curses screen, handling initialization, rendering, and input."""
    def __init__(self):
        self.stdscr = None
        self.widgets = []
        self.should_exit = False
        self.event_dispatcher = EventDispatcher()
        self._last_render_time = time.monotonic()

    def _init_curses_environment(self):
        """Initializes the curses screen."""
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, -1) # Use default background
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(4, curses.COLOR_RED, -1)

    def _destroy_curses_environment(self):
        """Restores the terminal to its original state."""
        if self.stdscr:
            curses.curs_set(1)
            self.stdscr.keypad(False)
            curses.echo()
            curses.nocbreak()
            curses.endwin()

    def add_widget(self, widget):
        """Adds a widget to the screen to be rendered."""
        self.widgets.append(widget)

    def remove_widget(self, widget):
        """Removes a widget from the screen."""
        self.widgets.remove(widget)

    def _handle_input(self):
        """Reads user input and posts it into the global event queue."""
        try:
            key = self.stdscr.getch()
            if key != -1:
                char = chr(key) if 32 <= key <= 126 else None
                self.event_dispatcher.post(create_key_event(key, char))
        except curses.error:
            pass

    def _render(self):
        """Renders all widgets to the screen."""
        self.stdscr.erase()
        max_y, max_x = self.stdscr.getmaxyx()
        for widget in self.widgets:
            widget.render(self.stdscr, max_y, max_x)
        self.stdscr.refresh()

        self._last_render_time = time.monotonic()
    def run(self, initial_setup_callback=None, main_loop_interval=0.016):
        """Runs the main event and rendering loop."""
        self._init_curses_environment()
        try:
            if initial_setup_callback:
                from lokutui.events import CustomEvent # Import CustomEvent here to avoid circular dependency
                initial_setup_callback()
            
            while not self.should_exit:
                self._handle_input()
                
                while _global_event_queue:
                    event = _global_event_queue.popleft()
                    if event.type == 'key' and event.data['code'] in [ord('q'), ord('Q')]:
                        self.should_exit = True
                        break
                    
                    self.event_dispatcher.dispatch(event)
                
                if time.monotonic() - self._last_render_time >= main_loop_interval:
                    from lokutui.events import CustomEvent # Import CustomEvent here too if needed
                    self.event_dispatcher.dispatch(CustomEvent('render_tick'))
                    self._render()
                
                time.sleep(0.001)
        finally:
            self._destroy_curses_environment()

    def exit(self):
        """Signals the application to exit."""
        self.should_exit = True


class Widget:
    """Base class for all TUI widgets."""
    def __init__(self, x=0, y=0, width=None, height=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        
    def render(self, stdscr, max_y, max_x):
        """Renders the widget to the given curses window."""
        if not self.visible:
            return
        pass