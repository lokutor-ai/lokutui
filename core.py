from __future__ import annotations
import curses
import time
from collections import deque
from lokutui.events import EventDispatcher, create_key_event, _global_event_queue


class Screen:
    def __init__(self):
        self.stdscr: object = None
        self.widgets: list[Widget] = []
        self.should_exit: bool = False
        self.event_dispatcher = EventDispatcher()
        self._last_render_time: float = time.monotonic()

    def _init_curses_environment(self) -> None:
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)

    def _destroy_curses_environment(self) -> None:
        if self.stdscr:
            curses.curs_set(1)
            self.stdscr.keypad(False)
            curses.echo()
            curses.nocbreak()
            curses.endwin()

    def add_widget(self, widget: Widget) -> None:
        self.widgets.append(widget)

    def remove_widget(self, widget: Widget) -> None:
        if widget in self.widgets:
            self.widgets.remove(widget)

    def _handle_input(self) -> None:
        try:
            key = self.stdscr.getch()
            if key != -1:
                char = chr(key) if 32 <= key <= 126 else None
                self.event_dispatcher.post(create_key_event(key, char))
        except (curses.error, ValueError):
            pass

    def _render(self) -> None:
        self.stdscr.erase()
        max_y, max_x = self.stdscr.getmaxyx()
        for widget in self.widgets:
            widget.render(self.stdscr, max_y, max_x)
        self.stdscr.refresh()

        self._last_render_time = time.monotonic()

    def run(self, initial_setup_callback: callable | None = None, main_loop_interval: float = 0.016) -> None:
        self._init_curses_environment()
        try:
            if initial_setup_callback:
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
                    from lokutui.events import CustomEvent 
                    self.event_dispatcher.dispatch(CustomEvent('render_tick'))
                    self._render()
                
                time.sleep(0.001)
        finally:
            self._destroy_curses_environment()

    def exit(self) -> None:
        self.should_exit = True


class Widget:
    def __init__(self, x: int = 0, y: int = 0, width: int | None = None, height: int | None = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible: bool = True
        
    def render(self, stdscr: object, max_y: int, max_x: int) -> None:
        if not self.visible:
            return
        pass

    def handle_event(self, event: object) -> bool:
        return False