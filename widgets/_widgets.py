from __future__ import annotations
from lokutui.core import Widget
from collections import deque
import curses

class Label(Widget):
    def __init__(self, text: str, x: int = 0, y: int = 0, color_pair: int = 1, width: int | None = None, height: int = 1):
        super().__init__(x, y, width, height)
        self.text = text
        self.color_pair = color_pair

    def render(self, stdscr: object, max_y: int, max_x: int) -> None:
        if not self.visible:
            return
        effective_width = self.width if self.width is not None else max_x - self.x
        render_y = min(self.y, max_y - 1)
        render_x = min(self.x, max_x - 1)
        if render_y < 0 or render_x < 0: 
            return
        display_text = str(self.text)
        if len(display_text) > effective_width:
            display_text = display_text[:effective_width]
        if len(display_text) > max_x - render_x: 
            display_text = display_text[:max_x - render_x]
        try:
            stdscr.addstr(render_y, render_x, display_text, curses.color_pair(self.color_pair))
        except curses.error: pass

class Box(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 10, height: int = 5, border_char: str = '─', corner_char: str = '+', color_pair: int = 1):
        super().__init__(x, y, width, height)
        self.border_char = border_char
        self.corner_char = corner_char
        self.color_pair = color_pair

    def render(self, stdscr: object, max_y: int, max_x: int) -> None:
        if not self.visible or self.width < 2 or self.height < 2:
            return
        end_y = min(self.y + self.height - 1, max_y - 1)
        end_x = min(self.x + self.width - 1, max_x - 1)
        actual_height = end_y - self.y + 1
        actual_width = end_x - self.x + 1
        if actual_width < 2 or actual_height < 2:
            return
        pair = curses.color_pair(self.color_pair)
        try:
            stdscr.addch(self.y, self.x, self.corner_char, pair)
            for i in range(1, actual_width - 1):
                stdscr.addch(self.y, self.x + i, self.border_char, pair)
            if actual_width > 1: 
                stdscr.addch(self.y, self.x + actual_width - 1, self.corner_char, pair)
            for j in range(1, actual_height - 1):
                stdscr.addch(self.y + j, self.x, '|', pair)
                if actual_width > 1:
                    stdscr.addch(self.y + j, self.x + actual_width - 1, '|', pair)
            if actual_height > 1: 
                stdscr.addch(self.y + actual_height - 1, self.x, self.corner_char, pair)
                for i in range(1, actual_width - 1):
                    stdscr.addch(self.y + actual_height - 1, self.x + i, self.border_char, pair)
                if actual_width > 1:
                    stdscr.addch(self.y + actual_height - 1, self.x + actual_width - 1, self.corner_char, pair)
        except curses.error: pass

class Button(Widget):
    def __init__(self, text: str, x: int = 0, y: int = 0, on_click: callable | None = None, color_pair: int = 1, highlight_color_pair: int = 3):
        super().__init__(x, y, width=len(text) + 4, height=1) 
        self._label = text
        self.on_click = on_click
        self.color_pair = color_pair
        self.highlight_color_pair = highlight_color_pair
        self.focused: bool = False

    @property
    def text(self) -> str:
        return self._label.center(self.width) if self.width else f"  {self._label}  "

    def handle_event(self, event: object) -> bool:
        if not self.focused or event.type != 'key':
            return False
        key = event.data['code']
        if key == ord('\n') or key == ord('\r') or key == ord(' '):
            if self.on_click:
                self.on_click()
            return True
        return False

    def render(self, stdscr: object, max_y: int, max_x: int) -> None:
        if not self.visible:
            return
        display_text = self.text
        render_y = min(self.y, max_y - 1)
        render_x = min(self.x, max_x - 1)
        if render_y < 0 or render_x < 0:
            return
        
        if len(display_text) > max_x - render_x:
            display_text = display_text[:max_x - render_x]
        
        if self.focused:
            attr = curses.color_pair(self.highlight_color_pair) | curses.A_BOLD | curses.A_REVERSE
        else:
            attr = curses.color_pair(self.color_pair)
            
        try:
            stdscr.addstr(render_y, render_x, display_text, attr)
        except curses.error: pass

class TextInput(Widget):
    def __init__(self, text: str = "", x: int = 0, y: int = 0, width: int = 20, color_pair: int = 1, highlight_color_pair: int = 3):
        super().__init__(x, y, width, height=1)
        self._text = text
        self.color_pair = color_pair
        self.highlight_color_pair = highlight_color_pair
        self.focused: bool = False
        self._cursor_pos = len(text) 

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = str(value)
        self._cursor_pos = len(self._text) 

    def handle_event(self, event: object) -> bool:
        if not self.focused or event.type != 'key':
            return False
        key = event.data['code']
        char = event.data.get('char')
        if char:
            self._text = self._text[:self._cursor_pos] + char + self._text[self._cursor_pos:]
            self._cursor_pos += 1
            return True
        elif key == curses.KEY_BACKSPACE or key == ord('\x7f') or key == ord('\x08'):
            if self._cursor_pos > 0:
                self._text = self._text[:self._cursor_pos - 1] + self._text[self._cursor_pos:]
                self._cursor_pos -= 1
            return True
        elif key == curses.KEY_DC:
            if self._cursor_pos < len(self._text):
                self._text = self._text[:self._cursor_pos] + self._text[self._cursor_pos + 1:]
            return True
        elif key == curses.KEY_LEFT or key == ord('h'):
            self._cursor_pos = max(0, self._cursor_pos - 1)
            return True
        elif key == curses.KEY_RIGHT or key == ord('l'):
            self._cursor_pos = min(len(self._text), self._cursor_pos + 1)
            return True
        return False

    def render(self, stdscr: object, max_y: int, max_x: int) -> None:
        if not self.visible:
            return
        render_y = min(self.y, max_y - 1)
        render_x = min(self.x, max_x - 1)
        if render_y < 0 or render_x < 0:
            return
        display_text = self._text
        start_display_idx = 0
        if len(display_text) > self.width:
            if self._cursor_pos > self.width - 1:
                start_display_idx = self._cursor_pos - (self.width - 1)
            display_text = display_text[start_display_idx : start_display_idx + self.width]
        display_text = display_text.ljust(self.width)
        
        if self.focused:
            attr = curses.color_pair(self.highlight_color_pair) | curses.A_BOLD
        else:
            attr = curses.color_pair(self.color_pair)

        try:
            stdscr.addstr(render_y, render_x, display_text, attr)
            if self.focused and render_y < max_y and render_x + (self._cursor_pos - start_display_idx) < max_x:
                curses.curs_set(1) 
                stdscr.move(render_y, render_x + (self._cursor_pos - start_display_idx))
            else:
                curses.curs_set(0) 
        except curses.error:
            curses.curs_set(0) 
            pass

class List(Widget):
    def __init__(self, items: list[str], x: int = 0, y: int = 0, width: int = 20, height: int = 5, color_pair: int = 1, highlight_color_pair: int = 3, on_select: callable | None = None):
        super().__init__(x, y, width, height)
        self.items = items
        self.selected_idx: int = 0
        self.color_pair = color_pair
        self.highlight_color_pair = highlight_color_pair
        self.on_select = on_select
        self.focused: bool = False
        self._scroll_offset: int = 0

    def handle_event(self, event: object) -> bool:
        if not self.focused or event.type != 'key' or not self.items:
            return False
        key = event.data['code']
        if key == curses.KEY_UP or key == ord('k'):
            self.selected_idx = max(0, self.selected_idx - 1)
            if self.selected_idx < self._scroll_offset:
                self._scroll_offset = self.selected_idx
            return True
        elif key == curses.KEY_DOWN or key == ord('j'):
            self.selected_idx = min(len(self.items) - 1, self.selected_idx + 1)
            if self.selected_idx >= self._scroll_offset + self.height:
                self._scroll_offset = self.selected_idx - self.height + 1
            return True
        elif key == ord('\n') or key == ord('\r'):
            if self.on_select:
                self.on_select(self.items[self.selected_idx])
            return True
        return False

    def render(self, stdscr: object, max_y: int, max_x: int) -> None:
        if not self.visible or self.width < 1 or self.height < 1:
            return
        render_y_start = min(self.y, max_y - 1)
        render_x_start = min(self.x, max_x - 1)
        actual_height = min(self.height, max_y - render_y_start)
        actual_width = min(self.width, max_x - render_x_start)
        for i in range(actual_height):
            item_idx = self._scroll_offset + i
            if item_idx >= len(self.items):
                break
            y_pos = render_y_start + i
            is_selected = (item_idx == self.selected_idx)
            
            indicator = "> " if is_selected else "  "
            display_text = (indicator + str(self.items[item_idx])).ljust(actual_width)[:actual_width]
            
            if is_selected:
                if self.focused:
                    attr = curses.color_pair(self.highlight_color_pair) | curses.A_BOLD | curses.A_REVERSE
                else:
                    attr = curses.color_pair(self.color_pair) | curses.A_BOLD
            else:
                attr = curses.color_pair(self.color_pair)
                
            try:
                stdscr.addstr(y_pos, render_x_start, display_text, attr)
            except curses.error: pass

class Select(Widget):
    def __init__(self, options: list[str], x: int = 0, y: int = 0, width: int = 20, color_pair: int = 1, highlight_color_pair: int = 3, on_change: callable | None = None):
        super().__init__(x, y, width, height=1)
        self.options = options
        self.selected_idx: int = 0
        self.color_pair = color_pair
        self.highlight_color_pair = highlight_color_pair
        self.on_change = on_change
        self.focused: bool = False

    def handle_event(self, event: object) -> bool:
        if not self.focused or event.type != 'key' or not self.options:
            return False
        key = event.data['code']
        if key == curses.KEY_LEFT or key == ord('h'):
            self.selected_idx = (self.selected_idx - 1 + len(self.options)) % len(self.options)
            if self.on_change:
                self.on_change(self.options[self.selected_idx])
            return True
        elif key == curses.KEY_RIGHT or key == ord('l') or key == ord(' ') or key == ord('\n') or key == ord('\r'):
            self.selected_idx = (self.selected_idx + 1) % len(self.options)
            if self.on_change:
                self.on_change(self.options[self.selected_idx])
            return True
        return False
    

    def render(self, stdscr: object, max_y: int, max_x: int) -> None:
        if not self.visible or self.width < 1:
            return
        render_y = min(self.y, max_y - 1)
        render_x = min(self.x, max_x - 1)
        if render_y < 0 or render_x < 0:
            return
        current_choice = self.options[self.selected_idx] if self.options else ""
        display_text = f"< {current_choice} >".center(self.width)[:self.width]
        color = curses.color_pair(self.highlight_color_pair) if self.focused else curses.color_pair(self.color_pair)
        try:
            stdscr.addstr(render_y, render_x, display_text, color)
        except curses.error: pass

class Checkbox(Widget):
    def __init__(self, label: str, x: int = 0, y: int = 0, checked: bool = False, color_pair: int = 1, highlight_color_pair: int = 3, on_change: callable | None = None):
        super().__init__(x, y, width=len(label) + 4, height=1)
        self.label = label
        self.checked = checked
        self.color_pair = color_pair
        self.highlight_color_pair = highlight_color_pair
        self.on_change = on_change
        self.focused: bool = False

    def handle_event(self, event: object) -> bool:
        if not self.focused or event.type != 'key':
            return False
        key = event.data['code']
        if key == ord(' ') or key == ord('\n') or key == ord('\r'):
            self.checked = not self.checked
            if self.on_change: self.on_change(self.checked)
            return True
        return False

    def render(self, stdscr: object, max_y: int, max_x: int) -> None:
        if not self.visible:
            return
        render_y = min(self.y, max_y - 1)
        render_x = min(self.x, max_x - 1)
        if render_y < 0 or render_x < 0:
            return
        box_str = "[X]" if self.checked else "[ ]"
        display_text = f"{box_str} {self.label}"
        color = curses.color_pair(self.highlight_color_pair) if self.focused else curses.color_pair(self.color_pair)
        try:
            stdscr.addstr(render_y, render_x, display_text, color)
        except curses.error: pass

class VStack(Widget):
    def __init__(self, widgets: list[Widget], x: int = 0, y: int = 0, spacing: int = 0):
        super().__init__(x, y)
        self.widgets = widgets
        self.spacing = spacing

    def render(self, stdscr: object, max_y: int, max_x: int) -> None:
        if not self.visible:
            return
        current_y = self.y
        for widget in self.widgets:
            widget.x, widget.y = self.x, current_y
            widget.render(stdscr, max_y, max_x)
            current_y += (widget.height if widget.height is not None else 1) + self.spacing

    def handle_event(self, event: object) -> bool:
        for widget in self.widgets:
            if widget.handle_event(event): return True
        return False

class HStack(Widget):
    def __init__(self, widgets: list[Widget], x: int = 0, y: int = 0, spacing: int = 1):
        super().__init__(x, y)
        self.widgets = widgets
        self.spacing = spacing

    def render(self, stdscr: object, max_y: int, max_x: int) -> None:
        if not self.visible:
            return
        current_x = self.x
        for widget in self.widgets:
            widget.x, widget.y = current_x, self.y
            widget.render(stdscr, max_y, max_x)
            current_x += (widget.width if widget.width is not None else 10) + self.spacing

    def handle_event(self, event: object) -> bool:
        for widget in self.widgets:
            if widget.handle_event(event): return True
        return False

class Frame(Box):
    def __init__(self, title: str = "", x: int = 0, y: int = 0, width: int = 10, height: int = 5, border_char: str = '─', corner_char: str = '+', color_pair: int = 1):
        super().__init__(x, y, width, height, border_char, corner_char, color_pair)
        self.title = title

    def render(self, stdscr: object, max_y: int, max_x: int) -> None:
        super().render(stdscr, max_y, max_x)
        if not self.visible or not self.title or self.width < 4:
            return
        display_title = f" {self.title} "
        if len(display_title) > self.width - 2:
            display_title = display_title[:self.width - 2]
        try:
            stdscr.addstr(self.y, self.x + 2, display_title, curses.color_pair(self.color_pair))
        except curses.error: pass

class Dialog(Widget):
    def __init__(self, title: str, message: str, on_yes: callable, on_no: callable):
        super().__init__()
        self.title = title
        self.message = message
        self.on_yes = on_yes
        self.on_no = on_no
        self.yes_btn = Button("YES", on_click=on_yes)
        self.no_btn = Button("NO", on_click=on_no)
        self.yes_btn.focused = True
        self.no_btn.focused = False

    def handle_event(self, event: object) -> bool:
        if event.type != 'key': return False
        key = event.data['code']
        if key in [ord('\t'), curses.KEY_BTAB, ord('h'), ord('l'), curses.KEY_LEFT, curses.KEY_RIGHT]:
            self.yes_btn.focused = not self.yes_btn.focused
            self.no_btn.focused = not self.no_btn.focused
            return True
        if self.yes_btn.focused and self.yes_btn.handle_event(event): return True
        if self.no_btn.focused and self.no_btn.handle_event(event): return True
        return True

    def render(self, stdscr: object, max_y: int, max_x: int) -> None:
        w, h = 50, 8
        x, y = (max_x - w) // 2, (max_y - h) // 2
        Frame(self.title, x, y, w, h, color_pair=4).render(stdscr, max_y, max_x)
        Label(self.message.center(w - 4), x + 2, y + 2, width=w - 4).render(stdscr, max_y, max_x)
        self.yes_btn.x, self.yes_btn.y = x + 10, y + 5
        self.no_btn.x, self.no_btn.y = x + 30, y + 5
        self.yes_btn.render(stdscr, max_y, max_x)
        self.no_btn.render(stdscr, max_y, max_x)

class LogDisplay(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 50, height: int = 10, color_pair: int = 1):
        super().__init__(x, y, width, height)
        self.messages = deque(maxlen=1000) 
        self.color_pair = color_pair
        self._scroll_offset: int = 0 
        self._auto_scroll: bool = True

    def add_message(self, message: str) -> None:
        self.messages.append(message)
        if self._auto_scroll: self._scroll_offset = 0 

    def render(self, stdscr: object, max_y: int, max_x: int) -> None:
        if not self.visible or self.width < 1 or self.height < 1:
            return
        render_y_start = min(self.y, max_y - 1)
        render_x_start = min(self.x, max_x - 1)
        actual_height = min(self.height, max_y - render_y_start)
        actual_width = min(self.width, max_x - render_x_start)
        start_message_idx = max(0, len(self.messages) - actual_height - self._scroll_offset)
        end_message_idx = max(0, len(self.messages) - self._scroll_offset)
        display_lines = list(self.messages)[start_message_idx:end_message_idx]
        for i, line in enumerate(reversed(display_lines)):
            y_pos = render_y_start + actual_height - 1 - i
            if y_pos < render_y_start: break
            try:
                stdscr.addstr(y_pos, render_x_start, line[:actual_width], curses.color_pair(self.color_pair))
            except curses.error: pass

class ProgressBar(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 30, percentage: float = 0.0, fill_char: str = '█', empty_char: str = '░', color_pair: int = 2):
        super().__init__(x, y, width, height=1)
        self._percentage = max(0.0, min(1.0, percentage)) 
        self.fill_char, self.empty_char, self.color_pair = fill_char, empty_char, color_pair

    @property
    def percentage(self) -> float: return self._percentage
    @percentage.setter
    def percentage(self, value: float) -> None: self._percentage = max(0.0, min(1.0, value)) 

    def render(self, stdscr: object, max_y: int, max_x: int) -> None:
        if not self.visible or self.width < 1: return
        render_y, render_x = min(self.y, max_y - 1), min(self.x, max_x - 1)
        actual_width = min(self.width, max_x - render_x)
        filled_cols = int(self._percentage * actual_width)
        bar_str = (self.fill_char * filled_cols) + (self.empty_char * (actual_width - filled_cols))
        try:
            stdscr.addstr(render_y, render_x, bar_str[:actual_width], curses.color_pair(self.color_pair))
        except curses.error: pass

class Chart(Widget):
    def __init__(self, x: int = 0, y: int = 0, width: int = 50, height: int = 10, series_data: dict[str, list[float]] | None = None, color_pairs: dict[str, int] | None = None, y_range: tuple[float, float] | None = None):
        super().__init__(x, y, width, height)
        self.series_data = series_data if series_data is not None else {} 
        self.color_pairs = color_pairs if color_pairs is not None else {label: i+1 for i, label in enumerate(self.series_data.keys())}
        self.y_range = y_range 
        self.grid_char = '.' 

    def _get_braille_char(self, points: list[bool]) -> str:
        bitmask = 0
        mapping = [0, 1, 2, 6, 3, 4, 5, 7]
        for i, dot in enumerate(points):
            if dot: bitmask |= (1 << mapping[i])
        return chr(0x2800 + bitmask)

    def render(self, stdscr: object, max_y: int, max_x: int) -> None:
        if not self.visible or self.width < 1 or self.height < 1: return
        ry, rx = min(self.y, max_y - 1), min(self.x, max_x - 1)
        ah, aw = min(self.height, max_y - ry), min(self.width, max_x - rx)
        for yo in range(ah):
            try: stdscr.addstr(ry + yo, rx, self.grid_char * aw, curses.color_pair(1))
            except curses.error: pass
        min_v, max_v = self.y_range if self.y_range else (float('inf'), float('-inf'))
        if not self.y_range:
            for s in self.series_data.values():
                if s: min_v, max_v = min(min_v, min(s)), max(max_v, max(s))
            if min_v == float('inf'): min_v, max_v = 0, 1 
        if max_v == min_v: max_v += 1.0
        grid = [[ [False] * 8 for _ in range(ah) ] for _ in range(aw)]
        for label, s in self.series_data.items():
            if not s: continue
            for cp in range(aw * 2):
                ci, dx = cp // 2, cp % 2 
                si = int(cp * (len(s) - 1) / (aw * 2 - 1)) if len(s) > 1 else 0
                nv = (s[si] - min_v) / (max_v - min_v)
                rp = int(nv * (ah * 4 - 1))
                ri, dy = ah - 1 - (rp // 4), 3 - (rp % 4)
                if 0 <= ri < ah and 0 <= ci < aw: grid[ci][ri][dx * 4 + dy] = True
        for yo in range(ah):
            for xo in range(aw):
                dots = grid[xo][yo]
                if any(dots):
                    label = list(self.series_data.keys())[0]
                    try: stdscr.addstr(ry + yo, rx + xo, self._get_braille_char(dots), curses.color_pair(self.color_pairs.get(label, 1)))
                    except curses.error: pass
