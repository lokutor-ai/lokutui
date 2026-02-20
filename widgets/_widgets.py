from lokutui.core import Widget
import curses

class Label(Widget):
    """A basic text label widget."""
    def __init__(self, text, x=0, y=0, color_pair=1, width=None, height=1):
        super().__init__(x, y, width, height)
        self.text = text
        self.color_pair = color_pair

    def render(self, stdscr, max_y, max_x):
        """Renders the label on the screen."""
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
        except curses.error:
            pass

class Box(Widget):
    """A simple box widget for layout or visual separation."""
    def __init__(self, x=0, y=0, width=10, height=5, border_char='─', corner_char='+', color_pair=1):
        super().__init__(x, y, width, height)
        self.border_char = border_char
        self.corner_char = corner_char
        self.color_pair = color_pair

    def render(self, stdscr, max_y, max_x):
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
        except curses.error:
            pass

class Button(Widget):
    """A clickable button widget."""
    def __init__(self, text, x=0, y=0, on_click=None, color_pair=1, highlight_color_pair=2):
        super().__init__(x, y, width=len(text) + 4, height=1) 
        self.text = f"  {text}  " 
        self.on_click = on_click
        self.color_pair = color_pair
        self.highlight_color_pair = highlight_color_pair
        self.focused = False

    def render(self, stdscr, max_y, max_x):
        if not self.visible:
            return
        
        display_text = self.text
        effective_width = self.width if self.width is not None else len(display_text)
        
        render_y = min(self.y, max_y - 1)
        render_x = min(self.x, max_x - 1)
        
        if render_y < 0 or render_x < 0:
            return

        if len(display_text) > effective_width:
            display_text = display_text[:effective_width]
        if len(display_text) > max_x - render_x:
            display_text = display_text[:max_x - render_x]
        
        current_color = curses.color_pair(self.highlight_color_pair) if self.focused else curses.color_pair(self.color_pair)
        
        try:
            stdscr.addstr(render_y, render_x, display_text, current_color)
        except curses.error:
            pass



class TextInput(Widget):
    """A basic single-line text input widget."""
    def __init__(self, text="", x=0, y=0, width=20, color_pair=1, highlight_color_pair=3):
        super().__init__(x, y, width, height=1)
        self._text = text
        self.color_pair = color_pair
        self.highlight_color_pair = highlight_color_pair
        self.focused = False
        self._cursor_pos = len(text) 

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)
        self._cursor_pos = len(self._text) 

    def render(self, stdscr, max_y, max_x):
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

        current_color = curses.color_pair(self.highlight_color_pair) if self.focused else curses.color_pair(self.color_pair)
        
        try:
            stdscr.addstr(render_y, render_x, display_text, current_color)
            if self.focused and render_y < max_y and render_x + (self._cursor_pos - start_display_idx) < max_x:
                curses.curs_set(1) 
                stdscr.move(render_y, render_x + (self._cursor_pos - start_display_idx))
            else:
                curses.curs_set(0) 
        except curses.error:
            curses.curs_set(0) 
            pass



class LogDisplay(Widget):
    """A widget to display a scrolling log of text messages."""
    def __init__(self, x=0, y=0, width=50, height=10, color_pair=1):
        super().__init__(x, y, width, height)
        self.messages = deque(maxlen=1000) 
        self.color_pair = color_pair
        self._scroll_offset = 0 
        self._auto_scroll = True

    def add_message(self, message):
        self.messages.append(message)
        if self._auto_scroll:
            self._scroll_offset = 0 

    def render(self, stdscr, max_y, max_x):
        if not self.visible or self.width < 1 or self.height < 1:
            return
        
        render_y_start = min(self.y, max_y - 1)
        render_x_start = min(self.x, max_x - 1)

        if render_y_start < 0 or render_x_start < 0:
            return

        actual_height = min(self.height, max_y - render_y_start)
        actual_width = min(self.width, max_x - render_x_start)

        if actual_width < 1 or actual_height < 1:
            return
        
        start_message_idx = max(0, len(self.messages) - actual_height - self._scroll_offset)
        end_message_idx = max(0, len(self.messages) - self._scroll_offset)
        
        display_lines = list(self.messages)[start_message_idx:end_message_idx]
        
        for i in range(len(display_lines)):
            line = display_lines[len(display_lines) - 1 - i] 
            y_pos = render_y_start + actual_height - 1 - i
            
            if y_pos < render_y_start: 
                break

            display_text = line[:actual_width] 
            
            try:
                stdscr.addstr(y_pos, render_x_start, display_text, curses.color_pair(self.color_pair))
            except curses.error:
                pass
        
    def scroll_up(self):
        self._scroll_offset = min(len(self.messages) - self.height, self._scroll_offset + 1)
        if self._scroll_offset > 0:
            self._auto_scroll = False

    def scroll_down(self):
        self._scroll_offset = max(0, self._scroll_offset - 1)
        if self._scroll_offset == 0:
            self._auto_scroll = True

class ProgressBar(Widget):
    """A simple horizontal progress bar."""
    def __init__(self, x=0, y=0, width=30, percentage=0.0, fill_char='█', empty_char='░', color_pair=2):
        super().__init__(x, y, width, height=1)
        self._percentage = max(0.0, min(1.0, percentage)) 
        self.fill_char = fill_char
        self.empty_char = empty_char
        self.color_pair = color_pair

    @property
    def percentage(self):
        return self._percentage

    @percentage.setter
    def percentage(self, value):
        self._percentage = max(0.0, min(1.0, value)) 

    def render(self, stdscr, max_y, max_x):
        if not self.visible or self.width < 1:
            return

        render_y = min(self.y, max_y - 1)
        render_x = min(self.x, max_x - 1)

        if render_y < 0 or render_x < 0:
            return
        
        actual_width = min(self.width, max_x - render_x)
        if actual_width < 1:
            return

        filled_cols = int(self._percentage * actual_width)
        bar_str = (self.fill_char * filled_cols) + (self.empty_char * (actual_width - filled_cols))
        bar_str = bar_str[:actual_width] 

        try:
            stdscr.addstr(render_y, render_x, bar_str, curses.color_pair(self.color_pair))
        except curses.error:
            pass

class Chart(Widget):
    """A basic line chart for displaying time-series data."""
    def __init__(self, x=0, y=0, width=50, height=10, series_data=None, color_pairs=None, y_range=None):
        super().__init__(x, y, width, height)
        self.series_data = series_data if series_data is not None else {} 
        self.color_pairs = color_pairs if color_pairs is not None else {label: i+1 for i, label in enumerate(series_data.keys())}
        self.y_range = y_range 
        self.grid_char = '.' 

        self.braille_lookup = {
            (False,False,False,False,False,False,False,False): 0x2800, 
            (True, False, False, False, False, False, False, False): 0x2801, 
            (False, True, False, False, False, False, False, False): 0x2802, 
            (True, True, False, False, False, False, False, False): 0x2803, 
            (False, False, True, False, False, False, False, False): 0x2804, 
            (True, False, True, False, False, False, False, False): 0x2805, 
            (False, True, True, False, False, False, False, False): 0x2806, 
            (True, True, True, False, False, False, False, False): 0x2807, 
            (False, False, False, True, False, False, False, False): 0x2808, 
            (True, False, False, True, False, False, False, False): 0x2809, 
            (False, True, False, True, False, False, False, False): 0x280a, 
            (True, True, False, True, False, False, False, False): 0x280b, 
            (False, False, True, True, False, False, False, False): 0x280c, 
            (True, False, True, True, False, False, False, False): 0x280d, 
            (False, True, True, True, False, False, False, False): 0x280e, 
            (True, True, True, True, False, False, False, False): 0x280f, 
            (False, False, False, False, True, False, False, False): 0x2810, 
            (True, False, False, False, True, False, False, False): 0x2811, 
            (False, True, False, False, True, False, False, False): 0x2812, 
            (True, True, False, False, True, False, False, False): 0x2813, 
            (False, False, True, False, True, False, False, False): 0x2814, 
            (True, False, True, False, True, False, False, False): 0x2815, 
            (False, True, True, False, True, False, False, False): 0x2816, 
            (True, True, True, False, True, False, False, False): 0x2817, 
            (False, False, False, True, True, False, False, False): 0x2818, 
            (True, False, False, True, True, False, False, False): 0x2819, 
            (False, True, False, True, True, False, False, False): 0x281a, 
            (True, True, False, True, True, False, False, False): 0x281b, 
            (False, False, True, True, True, False, False, False): 0x281c, 
            (True, False, True, True, True, False, False, False): 0x281d, 
            (False, True, True, True, True, False, False, False): 0x281e, 
            (True, True, True, True, True, False, False, False): 0x281f, 
            (False, False, False, False, False, True, False, False): 0x2820, 
            (True, False, False, False, False, True, False, False): 0x2821, 
            (False, True, False, False, False, True, False, False): 0x2822, 
            (True, True, False, False, False, True, False, False): 0x2823, 
            (False, False, True, False, False, True, False, False): 0x2824, 
            (True, False, True, False, False, True, False, False): 0x2825, 
            (False, True, True, False, False, True, False, False): 0x2826, 
            (True, True, True, False, False, True, False, False): 0x2827, 
            (False, False, False, True, False, True, False, False): 0x2828, 
            (True, False, False, True, False, True, False, False): 0x2829, 
            (False, True, False, True, False, True, False, False): 0x282a, 
            (True, True, False, True, False, True, False, False): 0x282b, 
            (False, False, True, True, False, True, False, False): 0x282c, 
            (True, False, True, True, False, True, False, False): 0x282d, 
            (False, True, True, True, False, True, False, False): 0x282e, 
            (True, True, True, True, False, True, False, False): 0x282f, 
            (False, False, False, False, True, True, False, False): 0x2830, 
            (True, False, False, False, True, True, False, False): 0x2831, 
            (False, True, False, False, True, True, False, False): 0x2832, 
            (True, True, False, False, True, True, False, False): 0x2833, 
            (False, False, True, False, True, True, False, False): 0x2834, 
            (True, False, True, False, True, True, False, False): 0x2835, 
            (False, True, True, False, True, True, False, False): 0x2836, 
            (True, True, True, False, True, True, False, False): 0x2837, 
            (False, False, False, True, True, True, False, False): 0x2838, 
            (True, False, False, True, True, True, False, False): 0x2839, 
            (False, True, False, True, True, True, False, False): 0x283a, 
            (True, True, False, True, True, True, False, False): 0x283b, 
            (False, False, True, True, True, True, False, False): 0x283c, 
            (True, False, True, True, True, True, False, False): 0x283d, 
            (False, True, True, True, True, True, False, False): 0x283e, 
            (True, True, True, True, True, True, False, False): 0x283f, 
            (False, False, False, False, False, False, True, False): 0x2840, 
            (False, False, False, False, False, False, False, True): 0x2880, 
            (True, False, False, False, False, False, True, False): 0x2841, 
            (True, False, False, False, False, False, False, True): 0x2881, 
            (False, True, False, False, False, False, True, False): 0x2842, 
            (False, True, False, False, False, False, False, True): 0x2882, 
            (True, True, False, False, False, False, True, False): 0x2843, 
            (True, True, False, False, False, False, False, True): 0x2883, 
            (False, False, True, False, False, False, True, False): 0x2844, 
            (False, False, True, False, False, False, False, True): 0x2884, 
            (True, False, True, False, False, False, True, False): 0x2845, 
            (True, False, True, False, False, False, False, True): 0x2885, 
            (False, True, True, False, False, False, True, False): 0x2846, 
            (False, True, True, False, False, False, False, True): 0x2886, 
            (True, True, True, False, False, False, True, False): 0x2847, 
            (True, True, True, False, False, False, False, True): 0x2887, 
            (False, False, False, True, False, False, True, False): 0x2848, 
            (False, False, False, True, False, False, False, True): 0x2888, 
            (True, False, False, True, False, False, True, False): 0x2849, 
            (True, False, False, True, False, False, False, True): 0x2889, 
            (False, True, False, True, False, False, True, False): 0x284a, 
            (False, True, False, True, False, False, False, True): 0x288a, 
            (True, True, False, True, False, False, True, False): 0x284b, 
            (True, True, False, True, False, False, False, True): 0x288b, 
            (False, False, True, True, False, False, True, False): 0x284c, 
            (False, False, True, True, False, False, False, True): 0x288c, 
            (True, False, True, True, False, False, True, False): 0x284d, 
            (True, False, True, True, False, False, False, True): 0x288d, 
            (False, True, True, True, False, False, True, False): 0x284e, 
            (False, True, True, True, False, False, False, True): 0x288e, 
            (True, True, True, True, False, False, True, False): 0x284f, 
            (True, True, True, True, False, False, False, True): 0x288f, 
            (False, False, False, False, True, True, True, False): 0x2850, 
            (False, False, False, False, True, True, False, True): 0x2890, 
            (True, False, False, False, True, True, True, False): 0x2851, 
            (True, False, False, False, True, True, False, True): 0x2891, 
            (False, True, False, False, True, True, True, False): 0x2852, 
            (False, True, False, False, True, True, False, True): 0x2892, 
            (True, True, False, False, True, True, True, False): 0x2853, 
            (True, True, False, False, True, True, False, True): 0x2893, 
            (False, False, True, False, True, True, True, False): 0x2854, 
            (False, False, True, False, True, True, False, True): 0x2894, 
            (True, False, True, False, True, True, True, False): 0x2855, 
            (True, False, True, False, True, True, False, True): 0x2895, 
            (False, True, True, False, True, True, True, False): 0x2856, 
            (False, True, True, False, True, True, False, True): 0x2896, 
            (True, True, True, False, True, True, True, False): 0x2857, 
            (True, True, True, False, True, True, False, True): 0x2897, 
            (False, False, False, True, True, True, True, False): 0x2858, 
            (False, False, False, True, True, True, False, True): 0x2898, 
            (True, False, False, True, True, True, True, False): 0x2859, 
            (True, False, False, True, True, True, False, True): 0x2899, 
            (False, True, False, True, True, True, True, False): 0x285a, 
            (False, True, False, True, True, True, False, True): 0x289a, 
            (True, True, False, True, True, True, True, False): 0x285b, 
            (True, True, False, True, True, True, False, True): 0x289b, 
            (False, False, True, True, True, True, True, False): 0x285c, 
            (False, False, True, True, True, True, False, True): 0x289c, 
            (True, False, True, True, True, True, True, False): 0x285d, 
            (True, False, True, True, True, True, False, True): 0x289d, 
            (False, True, True, True, True, True, True, False): 0x285e, 
            (False, True, True, True, True, True, False, True): 0x289e, 
            (True, True, True, True, True, True, True, False): 0x285f, 
            (True, True, True, True, True, True, False, True): 0x289f, 
            (False, False, False, False, False, False, True, True): 0x28C0, 
            (True, True, True, True, True, True, True, True): 0x28FF, 
        }
        self._reverse_braille_lookup = {v: k for k, v in self.braille_lookup.items()}


    def update_series(self, label, new_values):
        """Updates a data series with new values."""
        self.series_data[label] = new_values

    def add_series_point(self, label, value):
        """Adds a single point to an existing data series."""
        if label not in self.series_data:
            self.series_data[label] = []
        self.series_data[label].append(value)

    def _get_braille_char(self, points):
        """Converts up to 8 boolean points (pixels) into a Braille character."""
        bitmask = 0
        if points[0]: bitmask |= 0b00000001 
        if points[1]: bitmask |= 0b00000010 
        if points[2]: bitmask |= 0b00000100 
        if points[3]: bitmask |= 0b00001000 
        if points[4]: bitmask |= 0b00010000 
        if points[5]: bitmask |= 0b00100000 
        if points[6]: bitmask |= 0b01000000 
        if points[7]: bitmask |= 0b10000000 
        return chr(0x2800 + bitmask)

    def render(self, stdscr, max_y, max_x):
        if not self.visible or self.width < 1 or self.height < 1:
            return

        render_y_start = min(self.y, max_y - 1)
        render_x_start = min(self.x, max_x - 1)
        
        if render_y_start < 0 or render_x_start < 0:
            return

        actual_height = min(self.height, max_y - render_y_start)
        actual_width = min(self.width, max_x - render_x_start)

        if actual_width < 1 or actual_height < 1:
            return
        
        for y_offset in range(actual_height):
            try:
                stdscr.addstr(render_y_start + y_offset, render_x_start, self.grid_char * actual_width, curses.color_pair(1))
            except curses.error:
                pass

        min_val, max_val = self.y_range if self.y_range else (float('inf'), float('-inf'))
        if not self.y_range:
            for series in self.series_data.values():
                if series:
                    min_val = min(min_val, min(series))
                    max_val = max(max_val, max(series))
            if min_val == float('inf') or max_val == float('-inf'): 
                min_val, max_val = 0, 1 
        
        y_scale = actual_height / (max_val - min_val + 1e-9) 

        braille_grid = [[ [False] * 8 for _ in range(actual_height) ] for _ in range(actual_width)]

        for label, series in self.series_data.items():
            if not series:
                continue
            
            series_color = curses.color_pair(self.color_pairs.get(label, 1))

            num_points = len(series)
            if num_points == 0: continue

            for col_idx in range(actual_width):
                series_data_idx = int(col_idx * (num_points - 1) / (actual_width - 1)) if actual_width > 1 else 0
                if series_data_idx >= num_points: continue
                
                value = series[series_data_idx]
                
                y_pixel_pos = int((value - min_val) * y_scale)
                
                y_pixel_pos = max(0, min(y_pixel_pos, actual_height - 1))


                braille_y_coord = actual_height - 1 - y_pixel_pos 
                
                
                effective_braille_height = actual_height * 2
                braille_y_pos_fine = int((value - min_val) * (effective_braille_height / (max_val - min_val + 1e-9)))
                braille_y_pos_fine = max(0, min(braille_y_pos_fine, effective_braille_height - 1))
                
                char_row = actual_height - 1 - (braille_y_pos_fine // 2)
                dot_within_char_row = braille_y_pos_fine % 2 

                if 0 <= char_row < actual_height and 0 <= col_idx < actual_width:
                    if dot_within_char_row == 0: 
                        braille_grid[col_idx][char_row][2] = True 
                    else: 
                        braille_grid[col_idx][char_row][0] = True 
                
        for y_offset in range(actual_height):
            for x_offset in range(actual_width):
                dots = tuple(braille_grid[x_offset][y_offset])
                braille_char = self._get_braille_char(dots)
                try:
                    stdscr.addstr(render_y_start + y_offset, render_x_start + x_offset, braille_char, series_color)
                except curses.error:
                    pass


